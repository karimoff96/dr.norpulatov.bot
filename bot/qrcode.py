import segno
qrcode = segno.make("Green ave, Kingston")
qrcode.save('address.png', dark='darkred', light='lightblue', scale=10)