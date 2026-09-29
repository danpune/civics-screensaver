import ScreenSaver
import WebKit

// The whole screensaver is one web page, web/index.html, shown full screen. It needs no network.
@objc(CivicsSaverView)
final class CivicsSaverView: ScreenSaverView {
    private var web: WKWebView?

    override init?(frame: NSRect, isPreview: Bool) {
        super.init(frame: frame, isPreview: isPreview)
        wantsLayer = true
        layer?.backgroundColor = NSColor.black.cgColor
        // macOS does not always tell a screensaver to stop; this notice is the reliable signal.
        DistributedNotificationCenter.default().addObserver(self, selector: #selector(quiet),
            name: NSNotification.Name("com.apple.screensaver.willstop"), object: nil)
    }
    required init?(coder: NSCoder) { super.init(coder: coder) }

    override func startAnimation() {
        super.startAnimation()
        guard web == nil, let page = Bundle(for: CivicsSaverView.self).url(forResource: "index", withExtension: "html", subdirectory: "web") else { return }
        let w = WKWebView(frame: bounds)
        w.autoresizingMask = [.width, .height]
        w.setValue(false, forKey: "drawsBackground")   // no white flash before the page loads
        w.loadFileURL(page, allowingReadAccessTo: page.deletingLastPathComponent())
        addSubview(w)
        web = w
    }

    override func stopAnimation() { super.stopAnimation(); quiet() }

    @objc private func quiet() {   // stop the page's timers when the screensaver goes away
        web?.removeFromSuperview()
        web = nil
    }

    override func hitTest(_ point: NSPoint) -> NSView? { nil }   // a click wakes the Mac, it never reaches the page
    override var hasConfigureSheet: Bool { false }
    override var configureSheet: NSWindow? { nil }
}
