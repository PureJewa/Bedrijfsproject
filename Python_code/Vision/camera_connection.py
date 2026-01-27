import gxipy as gx
import numpy as np
import cv2


def apply_white_balance(img):
    """
    Simple gray-world white balance
    """
    result = img.astype(np.float32)

    avg_b = np.mean(result[:, :, 0])
    avg_g = np.mean(result[:, :, 1])
    avg_r = np.mean(result[:, :, 2])

    avg_gray = (avg_b + avg_g + avg_r) / 3

    result[:, :, 0] *= avg_gray / avg_b
    result[:, :, 1] *= avg_gray / avg_g
    result[:, :, 2] *= avg_gray / avg_r

    return np.clip(result, 0, 255).astype(np.uint8)


def main():
    print("-------------------------------------------------------------")
    print("GX Camera live feed – BayerRG10 → correct kleurbeeld")
    print("-------------------------------------------------------------")

    device_manager = gx.DeviceManager()
    dev_num, dev_info_list = device_manager.update_device_list()

    if dev_num == 0:
        print("Geen camera gevonden.")
        return

    cam = device_manager.open_device_by_index(1)

    cam.TriggerMode.set(gx.GxSwitchEntry.OFF)
    cam.ExposureTime.set(10000.0)
    cam.Gain.set(5.0)

    # Zet expliciet 10-bit Bayer
    cam.PixelFormat.set(gx.GxPixelFormatEntry.BAYER_RG10)

    cam.stream_on()
    print("Druk op 'q' om te stoppen")

    try:
        while True:
            raw_image = cam.data_stream[0].get_image()
            if raw_image is None:
                continue

            # RAW Bayer 10-bit
            bayer_10bit = raw_image.get_numpy_array()
            if bayer_10bit is None:
                continue

            # Normaliseer 10-bit → 8-bit
            bayer_8bit = (bayer_10bit >> 2).astype(np.uint8)

            # Debayering (correct RG pattern)
            frame = cv2.cvtColor(bayer_8bit, cv2.COLOR_BAYER_RG2RGB)

            # White balance (ESSENTIEEL)
            frame = apply_white_balance(frame)

            cv2.imshow("GX Camera Video Feed", frame)

            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

    finally:
        cam.stream_off()
        cam.close_device()
        cv2.destroyAllWindows()
        print("Camera correct afgesloten.")


if __name__ == "__main__":
    main()
