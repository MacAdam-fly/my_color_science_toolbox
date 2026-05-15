# CAM02 色貌模型实现（已移动到 color_agent 内部）
"""
CAM02 color appearance model implementation (migrated into color_agent utils).
Demo code is guarded under `if __name__ == "__main__"` to avoid running on import.
"""
import numpy as np

# 变换常数矩阵
M_CAT02 = np.array([[0.7328, 0.4296, -0.1624],
                    [-0.7036, 1.6975, 0.0061],
                    [0.0030, 0.0136, 0.9834]])
M_CAT02_inv = np.linalg.inv(M_CAT02)
M_HPE = np.array([[0.38971, 0.68898, -0.07868],
                    [-0.22981, 1.18340, 0.04641],
                    [0.00000, 0.00000, 1.00000]])
M_HPE_inv = np.linalg.inv(M_HPE)


class Cam02:
    SurroundFactor = {
        'AVERAGE': {'c': 0.69, 'Nc': 1.0, 'F': 1.0},
        'DIM': {'c': 0.59, 'Nc': 0.95, 'F': 0.9},
        'DARK': {'c': 0.525, 'Nc': 0.8, 'F': 0.8},
    }

    def __init__(self, LA, xyY, xyY_w, xyY_b, xyY_wr=None, surround='AVERAGE'):
        if xyY_wr is None:
            xyY_wr = [1/3, 1/3, 100]

        self.LA = LA
        self.x, self.y, self.Y = xyY
        self.x_w, self.y_w, self.Y_w = xyY_w
        self.x_b, self.y_b, self.Y_b = xyY_b
        self.x_wr, self.y_wr, self.Y_wr = xyY_wr
        self.surround_factors = Cam02.SurroundFactor[surround]
        self.c = self.surround_factors['c']
        self.Nc = self.surround_factors['Nc']
        self.F = self.surround_factors['F']

        self.XYZ = [(self.x * self.Y) / self.y, self.Y, ((1 - self.x - self.y) * self.Y) / self.y]
        self.XYZ_w = [(self.x_w * self.Y_w) / self.y_w, self.Y_w, ((1 - self.x_w - self.y_w) * self.Y_w) / self.y_w]
        self.XYZ_b = [(self.x_b * self.Y_b) / self.y_b, self.Y_b, ((1 - self.x_b - self.y_b) * self.Y_b) / self.y_b]
        self.XYZ_wr = [(self.x_wr * self.Y_wr) / self.y_wr, self.Y_wr, ((1 - self.x_wr - self.y_wr) * self.Y_wr) / self.y_wr]

        self.XYZ = np.array(self.XYZ)
        self.XYZ_w = np.array(self.XYZ_w)
        self.XYZ_b = np.array(self.XYZ_b)
        self.XYZ_wr = np.array(self.XYZ_wr)

    def __str__(self) -> str:
        return (f"Cam02(LA={self.LA}nit, xyY=({self.x}, {self.y}, {self.Y}), xyY_w=({self.x_w}, {self.y_w}, {self.Y_w}), "
                f"xyY_b=({self.x_b}, {self.y_b}, {self.Y_b}), xyY_wr=({self.x_wr}, {self.y_wr}, {self.Y_wr})"
                f",surround_factors={self.surround_factors})")

    def cal(self):
        LMS = np.dot(M_CAT02, self.XYZ)
        LMS_w = np.dot(M_CAT02, self.XYZ_w)
        LMS_wr = np.dot(M_CAT02, self.XYZ_wr)

        D = self.F * (1 - (1 / 3.6) * np.exp((-self.LA - 42) / 92))

        LMS_c = (self.Y_w * D / LMS_w + (1 - D)) * LMS
        LMS_wc = ((self.Y_w * D / LMS_w) + (1 - D)) * LMS_w

        k = 1 / (5 * self.LA + 1)
        FL = (0.2 * k ** 4) * (5 * self.LA) + 0.1 * ((1 - k ** 4) ** 2) * (5 * self.LA) ** (1 / 3)
        n = self.Y_b / self.Y_w
        Nbb = Ncb = 0.725 * (1 / n) ** 0.2
        z = 1.48 + np.sqrt(n)

        temp = np.dot(M_CAT02_inv, LMS_c)
        LMS_h = np.dot(M_HPE, temp)

        temp = np.dot(M_CAT02_inv, LMS_wc)
        LMS_wh = np.dot(M_HPE, temp)

        def nonlinear_compression(LMS_h, FL):
            LMS_ah = np.sign(LMS_h) * (
                        400 * (FL * np.abs(LMS_h) / 100) ** 0.42 / (27.13 + (FL * np.abs(LMS_h) / 100) ** 0.42) + 0.1)
            return LMS_ah

        LMS_ah = nonlinear_compression(LMS_h, FL)
        LMS_awh = nonlinear_compression(LMS_wh, FL)

        a = LMS_ah[0] - 12 * LMS_ah[1] / 11 + LMS_ah[2] / 11
        b = (1 / 9) * (LMS_ah[0] + LMS_ah[1] - 2 * LMS_ah[2])
        h = np.arctan2(b, a)
        h = h/np.pi*180 + 360 if h < 0 else h/np.pi*180

        e = 0.25 * (np.cos(h*np.pi/180 + 2) + 3.8)

        h_range = [20.14, 90, 164.25, 237.53, 380.14]
        H_range = [0, 100, 200, 300, 400]
        e_range = [0.8, 0.7, 1.0, 1.2, 0.8]
        if h < 20.14:
            h += 360
        H = None
        for i in range(4):
            if h_range[i] <= h < h_range[i + 1]:
                H = H_range[i] + (100*(h-h_range[i])/e_range[i]) / ((h-h_range[i])/e_range[i] + (h_range[i+1]-h)/e_range[i+1])
                break

        A = (2 * LMS_ah[0] + LMS_ah[1] + (1 / 20) * LMS_ah[2] - 0.305) * Nbb
        A_w = (2 * LMS_awh[0] + LMS_awh[1] + (1 / 20) * LMS_awh[2] - 0.305) * Nbb

        J = 100 * (A / A_w) ** (self.c * z)

        Q = (4 / self.c) * np.sqrt(J / 100) * (A_w+4) * FL ** 0.25

        t = (50000/13) * e * self.Nc * Ncb * np.sqrt(a ** 2 + b ** 2) / (LMS_ah[0] + LMS_ah[1] + 21 / 20 * LMS_ah[2])

        C = (t ** 0.9) * np.sqrt(J / 100) * (1.64 - 0.29 ** n) ** 0.73

        M = C * (FL ** 0.25)

        s = 100 * np.sqrt(M / Q)

        result = {
            'a': a,
            'b': b,
            'h': h,
            'H': H,
            'J': J,
            'Q': Q,
            'C': C,
            'M': M,
            's': s,
        }

        return result

    def inverse_cal(self, QMh):
        Q = QMh[0]
        M = QMh[1]
        h = QMh[2]

        D = self.F * (1 - (1 / 3.6) * np.exp((-self.LA - 42) / 92))
        k = 1 / (5 * self.LA + 1)
        FL = (0.2 * k ** 4) * (5 * self.LA) + 0.1 * ((1 - k ** 4) ** 2) * (5 * self.LA) ** (1 / 3)
        n = self.Y_b / self.Y_w
        Nbb = Ncb = 0.725 * (1 / n) ** 0.2
        z = 1.48 + np.sqrt(n)

        LMS_w = np.dot(M_CAT02, self.XYZ_w)
        LMS_wc = ((self.Y_w * D / LMS_w) + (1 - D)) * LMS_w
        temp = np.dot(M_CAT02_inv, LMS_wc)
        LMS_wh = np.dot(M_HPE, temp)

        def nonlinear_compression(LMS_h, FL):
            LMS_ah = np.sign(LMS_h) * (
                        400 * (FL * np.abs(LMS_h) / 100) ** 0.42 / (27.13 + (FL * np.abs(LMS_h) / 100) ** 0.42) + 0.1)
            return LMS_ah
        LMS_awh = nonlinear_compression(LMS_wh, FL)

        A_w = (2 * LMS_awh[0] + LMS_awh[1] + (1 / 20) * LMS_awh[2] - 0.305) * Nbb

        J = 6.25 * (self.c*Q/((A_w+4)*FL**0.25)) ** 2

        C = M/(FL**0.25)

        t = (C/(np.sqrt(J/100)*(1.64-0.29**n)**0.73))**(1/0.9)

        e = 0.25 * (np.cos(h*np.pi/180 + 2) + 3.8)

        A = A_w * (J/100)**(1/(self.c*z))

        p1 = 50000/13*self.Nc*Ncb*e/t

        p2 = (A/Nbb)+0.305

        p3 = 21/20

        hr = h*np.pi/180
        flag = abs(np.sin(hr)) > abs(np.cos(hr))
        if flag:
            p4 = p1/np.sin(hr)
            b_up = p2*(2+p3) * (460/1403)
            b_low = p4+(2+p3)*(220/1403)*(np.cos(hr)/np.sin(hr))-(27/1403)+p3*(6300/1403)
            b = b_up/b_low
            a = b*np.cos(hr)/np.sin(hr)
        else:
            p5 = p1/np.cos(hr)
            a_up = p2*(2+p3)*(460/1403)
            a_low = p5+(2+p3)*(220/1403)-(np.sin(hr)/np.cos(hr))*((27/1403)-p3*(6300/1403))
            a = a_up/a_low
            b = a*np.sin(hr)/np.cos(hr)

        M = np.array([[460, 451, 288],
                      [460, -891, -261],
                      [460, -220, -6300]])/1403
        LMS_ah = np.dot(M, [p2,a,b])

        def nonlinear_compression_inv(LMS_ah,FL):
            LMS_h = np.sign(LMS_ah-0.1) * (100/FL) * ((27.13*abs(LMS_ah-0.1)/(400-abs(LMS_ah-0.1)))**(1/0.42))
            return LMS_h

        LMS_h = nonlinear_compression_inv(LMS_ah,FL)

        temp = np.dot(M_HPE_inv, LMS_h)
        LMS_c = np.dot(M_CAT02, temp)

        LMS = LMS_c / ((self.Y_w * D / LMS_w) + (1 - D))

        XYZ = np.dot(M_CAT02_inv, LMS)

        return XYZ


if __name__ == "__main__":
    # demo usage guarded to avoid running on import
    cam02_red = Cam02(100, [0.7105, 0.2866, 117*0.2], [0.31, 0.32, 433], [0.31, 0.32, 433*0.01],surround='DIM')
    print("Red_XYZ",cam02_red.XYZ)
    print(cam02_red.cal())

    cam02_white = Cam02(100, [0.31, 0.32, 433*0.2], [0.31, 0.32, 433], [0.31, 0.32, 433*0.01],surround='DIM')
    print("White_XYZ",cam02_white.XYZ)
    print(cam02_white.cal())
