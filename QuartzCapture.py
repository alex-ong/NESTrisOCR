try:
    import Quartz
except ImportError:
    print('Please run "pip install pyobjc"')

try:
    from PIL import Image
except ImportError:
    print('Please run "pip install pillow"')


class QuartzCapture(object):
    def __init__(self):
        pass
    
    def ImageCapture(self, rectangle, window):
        x, y, w, h = rectangle

        if w <= 0 or h <= 0 or not window or not window['ID']:
            return None

        offsetX = window['x'] or 0
        offsetY = window['y'] or 0

        # can raise, correct later
        cgimg = Quartz.CGWindowListCreateImage(
            Quartz.CGRect(
                Quartz.CGPoint(offsetX + x, offsetY + y),
                Quartz.CGSize(w, h)
            ),
            Quartz.kCGWindowListOptionIncludingWindow | Quartz.kCGWindowListExcludeDesktopElements,
            window['ID'],
            0
        )

        width = Quartz.CGImageGetWidth(cgimg)
        height = Quartz.CGImageGetHeight(cgimg)
        pixeldata = Quartz.CGDataProviderCopyData(Quartz.CGImageGetDataProvider(cgimg))
        bpr = Quartz.CGImageGetBytesPerRow(cgimg)

        # Convert to PIL Image.  Note: CGImage's pixeldata is BGRA
        return Image.frombuffer("RGBA", (width, height), pixeldata, "raw", "BGRA", bpr, 1)


imgCap = QuartzCapture()

def ImageCapture(rectangle, window_dict):
    global imgCap
    return imgCap.ImageCapture(rectangle, window_dict)