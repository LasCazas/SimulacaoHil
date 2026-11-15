from PIL import Image

im = Image.open('Circuito_HIL/current_sch_render.png')
w, h = im.size

# Let's crop ESP32 + R1/C1 area
crop1 = im.crop((int(w * 0.15), int(h * 0.25), int(w * 0.65), int(h * 0.75)))
crop1.save('Circuito_HIL/crop_user_sch_esp.png')

# Let's crop PCM5102 area
crop2 = im.crop((int(w * 0.55), int(h * 0.15), int(w * 0.85), int(h * 0.50)))
crop2.save('Circuito_HIL/crop_user_sch_pcm.png')

print("Cropped areas saved!")
