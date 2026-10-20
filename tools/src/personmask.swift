// personmask: write per-frame person masks for a time window of a video, using Apple's built-in
// person segmentation (Vision framework; runs on the Neural Engine, no model download).
//
// usage: personmask <video> <start-seconds> <duration-seconds> <out-dir> [fast|balanced|accurate]
// Writes <out-dir>/000001.png ... as 8-bit grayscale masks (white = person), one per source frame.
import AVFoundation
import CoreImage
import Foundation
import ImageIO
import UniformTypeIdentifiers
import Vision

func fail(_ msg: String) -> Never {
    FileHandle.standardError.write((msg + "\n").data(using: .utf8)!)
    exit(1)
}

let args = CommandLine.arguments
if args.count < 5 { fail("usage: personmask <video> <start> <duration> <out-dir> [fast|balanced|accurate]") }
let url = URL(fileURLWithPath: args[1])
guard let start = Double(args[2]), let dur = Double(args[3]) else { fail("bad start/duration") }
let outDir = URL(fileURLWithPath: args[4], isDirectory: true)
let quality: VNGeneratePersonSegmentationRequest.QualityLevel = {
    switch args.count > 5 ? args[5] : "accurate" {
    case "fast": return .fast
    case "balanced": return .balanced
    default: return .accurate
    }
}()
try? FileManager.default.createDirectory(at: outDir, withIntermediateDirectories: true)

let asset = AVURLAsset(url: url)
let sem = DispatchSemaphore(value: 0)
var videoTrack: AVAssetTrack?
Task {
    videoTrack = try? await asset.loadTracks(withMediaType: .video).first
    sem.signal()
}
sem.wait()
guard let track = videoTrack else { fail("no video track") }
guard let reader = try? AVAssetReader(asset: asset) else { fail("cannot read video") }
let output = AVAssetReaderTrackOutput(track: track, outputSettings: [
    kCVPixelBufferPixelFormatTypeKey as String: kCVPixelFormatType_32BGRA,
])
reader.add(output)
let ts = CMTimeScale(600)
reader.timeRange = CMTimeRange(start: CMTime(seconds: start, preferredTimescale: ts),
                               duration: CMTime(seconds: dur, preferredTimescale: ts))
reader.startReading()

let request = VNGeneratePersonSegmentationRequest()
request.qualityLevel = quality
request.outputPixelFormat = kCVPixelFormatType_OneComponent8
let handler = VNSequenceRequestHandler()  // sequence handler = temporally stable masks across frames
let ctx = CIContext()
let gray = CGColorSpaceCreateDeviceGray()

var n = 0
while let sample = output.copyNextSampleBuffer() {
    guard let pb = CMSampleBufferGetImageBuffer(sample) else { continue }
    let w = CVPixelBufferGetWidth(pb), h = CVPixelBufferGetHeight(pb)
    do { try handler.perform([request], on: pb) } catch { fail("segmentation failed: \(error)") }
    guard let mask = request.results?.first?.pixelBuffer else { continue }
    // Scale the (lower-res) mask up to the frame size.
    let m = CIImage(cvPixelBuffer: mask)
    let sx = CGFloat(w) / m.extent.width, sy = CGFloat(h) / m.extent.height
    let scaled = m.transformed(by: CGAffineTransform(scaleX: sx, y: sy))
    guard let cg = ctx.createCGImage(scaled, from: CGRect(x: 0, y: 0, width: w, height: h), format: .L8, colorSpace: gray) else { continue }
    n += 1
    let file = outDir.appendingPathComponent(String(format: "%06d.png", n))
    guard let dest = CGImageDestinationCreateWithURL(file as CFURL, UTType.png.identifier as CFString, 1, nil) else { continue }
    CGImageDestinationAddImage(dest, cg, nil)
    CGImageDestinationFinalize(dest)
}
if reader.status == .failed { fail("reader failed: \(String(describing: reader.error))") }
print("frames \(n)")
