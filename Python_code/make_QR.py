import pandas as pd
import qrcode
for i in range(1,4):
    # Excel inlezen
    df = pd.read_excel(f"pad{i}.xlsx")

    # Alle onderdelen in één string zetten
    all_data = []
    for _, row in df.iterrows():
        # onderdeel_id, product, x, y, rotation
        all_data.append(f"{row['ID']}:{row['X']}:{row['Y']}")


    img = qrcode.make(all_data)
    img.save(f"Py.QR_plate_pad{i}.png")
    print(f"QR-code voor de hele plaat{i} is aangemaakt.")