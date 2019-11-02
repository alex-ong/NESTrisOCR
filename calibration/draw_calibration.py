from lib import getWindow, WindowCapture, screenPercToPixels, lerp, mult_rect
from OCRAlgo.DigitOCR import finalImageSize
from OCRAlgo.PieceStatsTextOCR import generate_stats
from OCRAlgo.PreviewOCR import calculateOffsets, PreviewImageSize
from PIL import Image, ImageDraw

#splits rectangle by digits.
#assumes 7 pixels with 1 pixel gaps.
def splitRect(perc, count):
    totalPixels = count * 7 + count - 1
    width = perc[2]
    singlePixel = width / totalPixels
    
    result = []
    for i in range(count):
        result.append([perc[0] + singlePixel * 8 * i,
                    perc[1],
                    7 * singlePixel,
                    perc[3]])
    return result


def captureArea(coords):
    hwnd = getWindow()
    if hwnd is None:
        return None
    return WindowCapture.ImageCapture(coords, hwnd)

def highlight_split_digits(c):    
    scorePix = mult_rect(c.CAPTURE_COORDS,c.scorePerc)
    linesPix = mult_rect(c.CAPTURE_COORDS,c.linesPerc)
    levelPix = mult_rect(c.CAPTURE_COORDS,c.levelPerc)
    
    scoreImg = captureArea(scorePix)
    linesImg = captureArea(linesPix)
    levelImg = captureArea(levelPix)

    scoreImg = scoreImg.resize(finalImageSize(6))
    linesImg = linesImg.resize(finalImageSize(3))
    levelImg = levelImg.resize(finalImageSize(2))

    return (scoreImg,linesImg,levelImg)

def highlight_preview(c):    
    previewPix = mult_rect(c.CAPTURE_COORDS,c.previewPerc)    
    previewImg = captureArea(previewPix)
    previewImg = previewImg.resize(PreviewImageSize, Image.BOX)
    return previewImg
    
def highlight_calibration(img, c):    
    poly = Image.new('RGBA', (img.width,img.height))
    draw = ImageDraw.Draw(poly)
    
    red = (255,0,0,128)    
    green = (0,255,0,128)
    blue = (0,100,255,128)       
    orange = (255,165,0,128)
    
    scorePerc, linesPerc, levelPerc = (c.scorePerc, c.linesPerc, c.levelPerc)
    
    
    for rect in splitRect(linesPerc, 3): #lines
        draw.rectangle(screenPercToPixels(img.width,img.height,rect),fill=red)
    
    for rect in splitRect(scorePerc, 6): #score
        draw.rectangle(screenPercToPixels(img.width,img.height,rect),fill=green) 

    for rect in splitRect(levelPerc, 2):
        draw.rectangle(screenPercToPixels(img.width,img.height,rect),fill=blue) #level

    if c.capture_field:
        fieldPerc = c.fieldPerc
        for x in range(10):
            for y in range(20):                
                blockPercX = lerp(fieldPerc[0], fieldPerc[0] + fieldPerc[2], x / 10.0 + 1 / 20.0)
                blockPercY = lerp(fieldPerc[1], fieldPerc[1] + fieldPerc[3], y / 20.0 + 1 / 40.0)
                rect = (blockPercX - 0.01, blockPercY - 0.01, 0.02, 0.02)
                draw.rectangle(screenPercToPixels(img.width,img.height,rect),fill=red)
        draw.rectangle(screenPercToPixels(img.width,img.height,c.color1Perc),fill=orange)
        draw.rectangle(screenPercToPixels(img.width,img.height,c.color2Perc),fill=orange)

    if c.capture_stats:
        if c.stats_method == 'TEXT':
            #pieces
            for value in generate_stats(c.CAPTURE_COORDS,c.statsPerc,c.scorePerc[3],False).values():
                draw.rectangle(screenPercToPixels(img.width,img.height,value),fill=orange)
        else: #c.stats_method == 'FIELD':
            stats2Perc = c.stats2Perc            
            for x in range(4):
                for y in range(2):                
                    blockPercX = lerp(stats2Perc[0], stats2Perc[0] + stats2Perc[2], x / 4.0 + 1 / 8.0)
                    blockPercY = lerp(stats2Perc[1], stats2Perc[1] + stats2Perc[3], y / 2.0 + 1 / 4.0)
                    rect = (blockPercX - 0.01, blockPercY - 0.01, 0.02, 0.02)
                    draw.rectangle(screenPercToPixels(img.width,img.height,rect),fill=blue)
    
    if c.capture_preview:
        draw.rectangle(screenPercToPixels(img.width,img.height,c.previewPerc),fill=blue)
        pixelWidth = c.previewPerc[2] / 31.0
        pixelHeight = c.previewPerc[3] / 15.0

        blockWidth = pixelWidth * 7
        blockHeight = pixelHeight * 7

        t1 = (c.previewPerc[0] + 4 * pixelWidth, c.previewPerc[1], blockWidth, blockHeight)
        t2 = (c.previewPerc[0] + 12 * pixelWidth, c.previewPerc[1], blockWidth, blockHeight)
        t3 = (c.previewPerc[0] + 20 * pixelWidth, c.previewPerc[1], blockWidth, blockHeight)
        t4 = (c.previewPerc[0] + 12 * pixelWidth, c.previewPerc[1] + pixelHeight * 8, blockWidth, blockHeight)
        for rect in [t1,t2,t3,t4]:
            draw.rectangle(screenPercToPixels(img.width,img.height,rect),fill=orange)
        for o in calculateOffsets():
            rect = (o[0], o[1], pixelWidth, pixelHeight)
            draw.rectangle(screenPercToPixels(img.width,img.height,rect),fill='red')

    img.paste(poly,mask=poly)    
    del draw


#todo, return image or array of images with cropped out sections.
def draw_calibration(config):
    hwnd = getWindow()
    if hwnd is None:
        print("Unable to find window with title:",  config.WINDOW_NAME)
        return None
    
    img = WindowCapture.ImageCapture(config.CAPTURE_COORDS, hwnd)
    if config.captureMethod == 'FILE':
        for i in range(10):
           WindowCapture.NextFrame()
    highlight_calibration(img, config)   
    img = img.resize((512,448),Image.ANTIALIAS)
    return img

