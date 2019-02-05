from PIL import Image
from PIL import ImageFont
from PIL import ImageDraw 

for i in range (10000):
    img = Image.new('RGB', (94, 14), color = (0,0,0))
    draw = ImageDraw.Draw(img)
    font = ImageFont.truetype("PressStart2P.ttf", 16)
    # draw.text((x, y),"Sample Text",(r,g,b))
    draw.text((0,0),"{:06d}".format(i*100),(255,255,255),font=font)
    img.save("test/"+("{:06d}".format(i*100))+'.png')