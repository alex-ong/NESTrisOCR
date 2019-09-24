from lib import getWindow, WindowCapture, screenPercToPixels, lerp
from OCRAlgo.PieceStatsTextOCR import generate_stats
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

def highlight_calibration(img, c):    
    poly = Image.new('RGBA', (img.width,img.height))
    draw = ImageDraw.Draw(poly)
    
    red = (255,0,0,128)    
    green = (0,255,0,128)
    blue = (0,0,255,128)       
    orange = (255,165,0,128)
    
    scorePerc, linesPerc, levelPerc = (c.scorePerc, c.linesPerc, c.levelPerc)
    
    
    for rect in splitRect(linesPerc, 3): #lines
        draw.rectangle(screenPercToPixels(img.width,img.height,rect),fill=red)
    
    for rect in splitRect(scorePerc, 6): #score
        draw.rectangle(screenPercToPixels(img.width,img.height,rect),fill=green) 

    for rect in splitRect(levelPerc, 2):
        draw.rectangle(screenPercToPixels(img.width,img.height,rect),fill=blue) #level

    if c.capture_stats:
        if c.stats_method == 'TEXT':
            #pieces
            #draw.rectangle(screenPercToPixels(img.width,img.height,c.statsPerc),fill=blue)
            for value in generate_stats(c.CAPTURE_COORDS,c.statsPerc,c.scorePerc[3],False).values():
                draw.rectangle(screenPercToPixels(img.width,img.height,value),fill=orange)
        else: #c.stats_method == 'FIELD':
            stats2Perc = c.stats2Perc
            draw.rectangle(screenPercToPixels(img.width,img.height,stats2Perc),fill=blue)
            for x in range(4):
                for y in range(2):                
                    blockPercX = lerp(stats2Perc[0], stats2Perc[0] + stats2Perc[2], x / 4.0 + 1 / 8.0)
                    blockPercY = lerp(stats2Perc[1], stats2Perc[1] + stats2Perc[3], y / 2.0 + 1 / 4.0)
                    rect = (blockPercX - 0.01, blockPercY - 0.01, 0.02, 0.02)
                    draw.rectangle(screenPercToPixels(img.width,img.height,rect),fill=red)
        
    img.paste(poly,mask=poly)    
    del draw

#todo, return image or array of images with cropped out sections.
def draw_calibration(config):
    hwnd = getWindow()
    if hwnd is None:
        print("Unable to find window with title:",  config.WINDOW_NAME)
        return None
    
    img = WindowCapture.ImageCapture(config.CAPTURE_COORDS, hwnd)
    highlight_calibration(img, config)   
    img.thumbnail((512,480),Image.NEAREST)
    return img
    