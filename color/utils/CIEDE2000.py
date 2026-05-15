# CIEDE2000 色差计算（迁移到 color_agent/utils）
import numpy as np


class CIEDE2000:
    @staticmethod
    def calculate(lab1, lab2, kL=1.0, kC=1.0, kH=1.0):
        lab1 = np.array(lab1, dtype=np.float64)
        lab2 = np.array(lab2, dtype=np.float64)

        if lab1.ndim == 1:
            lab1 = lab1.reshape(1, 3)
        if lab2.ndim == 1:
            lab2 = lab2.reshape(1, 3)

        if lab1.shape != lab2.shape:
            raise ValueError("lab1和lab2的形状必须相同")

        L1, a1, b1 = lab1[:, 0], lab1[:, 1], lab1[:, 2]
        L2, a2, b2 = lab2[:, 0], lab2[:, 1], lab2[:, 2]

        C1 = np.sqrt(a1 ** 2 + b1 ** 2)
        C2 = np.sqrt(a2 ** 2 + b2 ** 2)
        C_avg = (C1 + C2) / 2

        G = 0.51 * (1 - np.sqrt(C_avg ** 7 / (C_avg ** 7 + 25 ** 7)))

        a1_prime = a1 * (1 + G)
        a2_prime = a2 * (1 + G)

        C1_prime = np.sqrt(a1_prime ** 2 + b1 ** 2)
        C2_prime = np.sqrt(a2_prime ** 2 + b2 ** 2)

        h1_prime = np.arctan2(b1, a1_prime)
        h2_prime = np.arctan2(b2, a2_prime)
        h1_prime = np.degrees(h1_prime) % 360
        h2_prime = np.degrees(h2_prime) % 360

        delta_L_prime = L2 - L1
        delta_C_prime = C2_prime - C1_prime

        delta_h_prime = h2_prime - h1_prime
        delta_h_prime = np.where(np.abs(delta_h_prime) <= 180,
                                 delta_h_prime,
                                 np.where(delta_h_prime > 180,
                                          delta_h_prime - 360,
                                          delta_h_prime + 360))

        delta_H_prime = 2 * np.sqrt(C1_prime * C2_prime) * np.sin(np.radians(delta_h_prime / 2))

        L_prime_avg = (L1 + L2) / 2
        C_prime_avg = (C1_prime + C2_prime) / 2

        h_prime_sum = h1_prime + h2_prime
        h_prime_avg_condition = np.abs(h1_prime - h2_prime) <= 180

        h_prime_avg = np.where(h_prime_avg_condition,
                               h_prime_sum / 2,
                               np.where(h_prime_sum < 360,
                                        (h_prime_sum + 360) / 2,
                                        (h_prime_sum - 360) / 2))

        T = (1 - 0.17 * np.cos(np.radians(h_prime_avg - 30)) +
             0.24 * np.cos(np.radians(2 * h_prime_avg)) +
             0.32 * np.cos(np.radians(3 * h_prime_avg + 6)) -
             0.20 * np.cos(np.radians(4 * h_prime_avg - 63)))

        delta_theta = 30 * np.exp(-((h_prime_avg - 275) / 25) ** 2)

        R_C = 2 * np.sqrt(C_prime_avg ** 7 / (C_prime_avg ** 7 + 25 ** 7))

        S_L = 1 + (0.015 * (L_prime_avg - 50) ** 2) / np.sqrt(20 + (L_prime_avg - 50) ** 2)

        S_C = 1 + 0.045 * C_prime_avg

        S_H = 1 + 0.015 * C_prime_avg * T

        R_T = -np.sin(np.radians(2 * delta_theta)) * R_C

        term1 = (delta_L_prime / (kL * S_L)) ** 2
        term2 = (delta_C_prime / (kC * S_C)) ** 2
        term3 = (delta_H_prime / (kH * S_H)) ** 2
        term4 = R_T * (delta_C_prime / (kC * S_C)) * (delta_H_prime / (kH * S_H))

        delta_E = np.sqrt(term1 + term2 + term3 + term4)

        return delta_E[0] if delta_E.size == 1 else delta_E

    @staticmethod
    def batch_calculate(lab_array1, lab_array2, kL=1.0, kC=1.0, kH=1.0):
        return CIEDE2000.calculate(lab_array1, lab_array2, kL, kC, kH)

    @staticmethod
    def from_XYZ(XYZ1, XYZ2, white_point=None, kL=1.0, kC=1.0, kH=1.0):
        if white_point is None:
            white_point = np.array([0.95047, 1.0, 1.08883])

        lab1 = CIEDE2000._XYZ_to_Lab(XYZ1, white_point)
        lab2 = CIEDE2000._XYZ_to_Lab(XYZ2, white_point)

        return CIEDE2000.calculate(lab1, lab2, kL, kC, kH)

    @staticmethod
    def _XYZ_to_Lab(XYZ, white_point):
        XYZ = np.array(XYZ, dtype=np.float64)
        white_point = np.array(white_point, dtype=np.float64)

        XYZ_norm = XYZ / white_point

        f_XYZ = np.where(XYZ_norm > 0.008856,
                         XYZ_norm ** (1 / 3),
                         7.787 * XYZ_norm + 16 / 116)

        L = 116 * f_XYZ[1] - 16
        a = 500 * (f_XYZ[0] - f_XYZ[1])
        b = 200 * (f_XYZ[1] - f_XYZ[2])

        return np.array([L, a, b])
