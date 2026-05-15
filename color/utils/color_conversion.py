"""
    两个空间被封装在类中，方便调用
"""
import numpy as np


class LabColorConverter:
    """
    A comprehensive color space conversion class supporting:
    - XYZ <-> CIE Lab
    - CIE Lab <-> CIE LCH
    - XYZ <-> xyY

    Reference whites are configurable (D50/D65 by default)
    """

    def __init__(self, reference_white=None):
        """
        Initialize converter with reference white point

        :param reference_white: Predefined illuminant ('D50'/'D65') or
               custom XYZ triplet (e.g., [X,Y,Z])
        """
        if reference_white is None:
            self.XYZw = np.array([96.42, 100.0, 82.5])
        else:
            self.XYZw = np.asarray(reference_white)

    @staticmethod
    def _f(t):
        """L*计算使用的分段函数"""
        if t > 0.008856:
            return t ** (1 / 3)
        else:
            return (841 / 108) * t + 16 / 116

    @staticmethod
    def _f_inverse(fy):
        """L*逆计算使用的分段函数"""
        if fy > 6 / 29:
            return fy ** 3
        else:
            return (fy - 16 / 116) * 3 * (6 / 29) ** 2

    def XYZ_to_lab(self, xyz):
        """
        Convert XYZ color to CIE Lab color space

        :param xyz: Input XYZ values (array-like)
        :return: CIE Lab values [L*, a*, b*]
        """
        xyz = np.asarray(xyz)
        Xw, Yw, Zw = self.XYZw

        x_ratio = xyz[0] / Xw
        y_ratio = xyz[1] / Yw
        z_ratio = xyz[2] / Zw

        L = 116 * LabColorConverter._f(y_ratio) -16
        a = 500 * (LabColorConverter._f(x_ratio) - LabColorConverter._f(y_ratio))
        b = 200 * (LabColorConverter._f(y_ratio) - LabColorConverter._f(z_ratio))

        return np.array([L, a, b])

    def lab_to_XYZ(self, lab):
        """
        Convert CIE Lab color to XYZ color space

        :param lab: Input Lab values [L*, a*, b*] (array-like)
        :return: XYZ values
        """
        lab = np.asarray(lab)
        Xw, Yw, Zw = self.XYZw


        fy = (lab[0] + 16) / 116
        fx = lab[1] / 500 + fy
        fz = fy - lab[2] / 200

        return np.array([
            Xw * LabColorConverter._f_inverse(fx),
            Yw * LabColorConverter._f_inverse(fy),
            Zw * LabColorConverter._f_inverse(fz)
        ])

    def Y_to_L(self, Y):
        """
        Convert Y to L* in CIE Lab color space

        :param Y: Input Y value (array-like)
        :return: L* value
        """
        return 116 * self._f(Y) - 16

    @staticmethod
    def lab_to_lch(lab):
        """
        Convert CIE Lab to LCH(ab) color space (static method)

        :param lab: Input Lab values [L*, a*, b*] (array-like)
        :return: LCH values [L*, C*, h°]
        """
        lab = np.asarray(lab)
        a, b = lab[1], lab[2]
        C = np.hypot(a, b)
        h = np.degrees(np.arctan2(b, a)) % 360.0
        return np.array([lab[0], C, h])

    @staticmethod
    def lch_to_lab(lch):
        """
        Convert LCH(ab) to CIE Lab color space (static method)

        :param lch: Input LCH values [L*, C*, h°] (array-like)
        :return: Lab values [L*, a*, b*]
        """
        lch = np.asarray(lch)
        h = np.radians(lch[2])
        return np.array([
            lch[0],
            lch[1] * np.cos(h),
            lch[1] * np.sin(h)
        ])

    @staticmethod
    def XYZ_to_xyY(XYZ):
        """
        Convert XYZ to xyY color space (static method)

        :param xyz: Input XYZ values (array-like)
        :return: xyY values [x, y, Y]
        """
        XYZ = np.asarray(XYZ)
        sum_xyz = np.sum(XYZ)
        if sum_xyz == 0:
            return np.array([0.0, 0.0, 0.0])
        return np.array([
            XYZ[0] / sum_xyz,
            XYZ[1] / sum_xyz,
            XYZ[1]
        ])

    @staticmethod
    def xyY_to_XYZ(xyY):
        """
        Convert xyY to XYZ color space (static method)

        :param xyY: Input xyY values [x, y, Y] (array-like)
        :return: XYZ values
        """
        x, y, Y = xyY
        if y == 0:
            return np.array([0.0, Y, 0.0])
        return np.array([
            (x / y) * Y,
            Y,
            ((1 - x - y) / y) * Y
        ])


class LuvColorConverter:
    """
    CIE L*u*v* 颜色空间转换器
    提供XYZ、L*u*v*、LCH_uv、LsH之间的转换方法
    """

    def __init__(self, reference_white=None):
        """
        Initialize converter with reference white point

        :param reference_white: Predefined illuminant ('D50'/'D65') or
               custom XYZ triplet (e.g., [X,Y,Z])
        """
        if reference_white is None:
            self.XYZw = np.array([96.42, 100.0, 82.5])
        else:
            self.XYZw = np.asarray(reference_white)

    def compute_un_vn(self):
        """计算参考白点的u'_n和v'_n"""
        Xt, Yt, Zt = self.XYZw
        D_n = Xt + 15 * Yt + 3 * Zt
        if D_n == 0:
            return 0.0, 0.0
        return 4 * Xt / D_n, 9 * Yt / D_n

    @staticmethod
    def _f(t):
        """L*计算使用的分段函数"""
        if t > 0.008856:
            return t ** (1 / 3)
        else:
            return (841 / 108) * t + 16 / 116

    @staticmethod
    def _f_inverse(fy):
        """L*逆计算使用的分段函数"""
        if fy > 6 / 29:
            return fy ** 3
        else:
            return (fy - 16 / 116) * 3 * (6 / 29) ** 2

    def XYZ_to_luv(self,XYZ):
        """
        XYZ到L*u*v*的转换
        参数：
            XYZ: 形如[X, Y, Z]的数组
            XYZw: 参考白点的XYZ值
        返回：
            Luv: 形如[L*, u*, v*]的numpy数组
        """
        Xt, Yt, Zt = self.XYZw
        X, Y, Z = XYZ

        # 计算参考白点的u'_n和v'_n
        u_n, v_n = self.compute_un_vn()

        # 计算当前XYZ的u'和v'
        D = X + 15 * Y + 3 * Z
        if D == 0:
            u, v = 0.0, 0.0
        else:
            u = 4 * X / D
            v = 9 * Y / D

        # 计算L*
        t_y = Y / Yt if Yt != 0 else 0
        L = 116 * LuvColorConverter._f(t_y) - 16 if Yt != 0 else 0

        # 计算u*和v*
        u_star = 13 * L * (u - u_n) if L != 0 else 0
        v_star = 13 * L * (v - v_n) if L != 0 else 0

        return np.array([L, u_star, v_star])

    def luv_to_XYZ(self, Luv):
        """
        L*u*v*到XYZ的转换
        参数：
            Luv: 形如[L*, u*, v*]的数组
            XYZw: 参考白点的XYZ值
        返回：
            XYZ: 形如[X, Y, Z]的numpy数组
        """
        Xt, Yt, Zt = self.XYZw
        L, u_star, v_star = Luv

        if L == 0:
            return np.array([0.0, 0.0, 0.0])

        # 计算参考白点的u'_n和v'_n
        u_n, v_n = self.compute_un_vn()

        # 计算u'和v'
        u_prime = u_star / (13 * L) + u_n
        v_prime = v_star / (13 * L) + v_n

        # 计算Y
        fy = (L + 16) / 116
        Y = Yt * LuvColorConverter._f_inverse(fy)

        if Y == 0:
            return np.array([0.0, 0.0, 0.0])

        # 计算X和Z
        if v_prime == 0:
            X, Z = 0.0, 0.0
        else:
            X = (9 * u_prime * Y) / (4 * v_prime)
            Z = ((9 * Y / v_prime) - X - 15 * Y) / 3

        return np.array([X, Y, Z])

    @staticmethod
    def luv_to_lch(Luv):
        """
        L*u*v*到LCH_uv的转换
        参数：
            Luv: 形如[L*, u*, v*]的数组
        返回：
            LCH: 形如[L*, C_uv, h_uv]的numpy数组，h_uv单位为度
        """
        L, u, v = Luv
        C = np.sqrt(u ** 2 + v ** 2)
        h = np.arctan2(v, u)
        h_deg = np.degrees(h) % 360
        return np.array([L, C, h_deg])

    @staticmethod
    def lch_to_luv(LCH):
        """
        LCH_uv到L*u*v*的转换
        参数：
            LCH: 形如[L*, C_uv, h_uv]的数组，h_uv单位为度
        返回：
            Luv: 形如[L*, u*, v*]的numpy数组
        """
        L, C, h_deg = LCH
        h_rad = np.radians(h_deg)
        return np.array([L, C * np.cos(h_rad), C * np.sin(h_rad)])

    @staticmethod
    def luv_to_lsh(Luv):
        """
        L*u*v*到LsH的转换
        参数：
            Luv: 形如[L*, u*, v*]的数组
        返回：
            LsH: 形如[L*, s_uv, h_uv]的numpy数组，h_uv单位为度
        """
        L, u, v = Luv
        C = np.sqrt(u ** 2 + v ** 2)
        s = C / L if L != 0 else 0.0
        h = np.arctan2(v, u)
        h_deg = np.degrees(h) % 360
        return np.array([L, s, h_deg])

    @staticmethod
    def lsh_to_luv(LsH):
        """
        LsH到L*u*v*的转换
        参数：
            LsH: 形如[L*, s_uv, h_uv]的数组，h_uv单位为度
        返回：
            Luv: 形如[L*, u*, v*]的numpy数组
        """
        L, s, h_deg = LsH
        h_rad = np.radians(h_deg)
        C = s * L
        return np.array([L, C * np.cos(h_rad), C * np.sin(h_rad)])

    @staticmethod
    def XYZ_to_xyY(XYZ):
        """
        Convert XYZ to xyY color space (static method)

        :param xyz: Input XYZ values (array-like)
        :return: xyY values [x, y, Y]
        """
        XYZ = np.asarray(XYZ)
        sum_xyz = np.sum(XYZ)
        if sum_xyz == 0:
            return np.array([0.0, 0.0, 0.0])
        return np.array([
            XYZ[0] / sum_xyz,
            XYZ[1] / sum_xyz,
            XYZ[1]
        ])

    @staticmethod
    def xyY_to_XYZ(xyY):
        """
        Convert xyY to XYZ color space (static method)

        :param xyY: Input xyY values [x, y, Y] (array-like)
        :return: XYZ values
        """
        x, y, Y = xyY
        if y == 0:
            return np.array([0.0, Y, 0.0])
        return np.array([
            (x / y) * Y,
            Y,
            ((1 - x - y) / y) * Y
        ])


class LMS2006Converter:
    """
    A class for converting between LMS and XYZ color spaces for 2° or 10° field of view (FOV).

    Attributes:
        fov (int): Field of view in degrees, must be either 2 or 10
        matrix (np.ndarray): 3x3 conversion matrix for LMS to XYZ
        inverse_matrix (np.ndarray): 3x3 inverse matrix for XYZ to LMS conversion
    """

    def __init__(self, fov: int = 10):
        """
        Initialize color converter with specified field of view.

        Args:
            fov (int): Visual field angle (2 or 10 degrees). Defaults to 10.

        Raises:
            ValueError: If invalid FOV value is provided
        """
        if fov not in (2, 10):
            raise ValueError("Invalid FOV value. Supported values: 2 or 10")

        # Define conversion matrices based on FOV
        if fov == 10:
            self.matrix = np.array([
                [1.93986443, -1.34664359, 0.43044935],
                [0.69283932, 0.34967567, 0],
                [0, 0, 2.14687945]
            ])
        else:  # 2° FOV
            self.matrix = np.array([
                [1.94735469, -1.41445123, 0.36476327],
                [0.68990272, 0.34832189, 0],
                [0, 0, 1.93485343]
            ])

        self.inverse_matrix = np.linalg.inv(self.matrix)

    def lms_to_xyz(self, lms: np.ndarray) -> np.ndarray:
        """
        Convert from LMS color space to XYZ color space.

        Args:
            lms (np.ndarray): Input LMS values as a 1D array of shape (3,)

        Returns:
            np.ndarray: Converted XYZ values as a 1D array
        """
        return np.dot(self.matrix, lms)

    def xyz_to_lms(self, xyz: np.ndarray) -> np.ndarray:
        """
        Convert from XYZ color space to LMS color space.

        Args:
            xyz (np.ndarray): Input XYZ values as a 1D array of shape (3,)

        Returns:
            np.ndarray: Converted LMS values as a 1D array
        """
        return np.dot(self.inverse_matrix, xyz)



# 使用案例
def labColorConverter_use():
    # Create an instance of LabColorConverter with D65 reference white
    lab_converter = LabColorConverter(reference_white='D65')
    # lab_converter = LabColorConverter(reference_white=[95.047, 100.0, 108.883]) #可以直接指定参考白

    # Define an XYZ color
    xyz_color = np.array([10, 10, 10])

    # Convert XYZ to Lab
    lab_color = lab_converter.XYZ_to_lab(xyz_color)
    print(f"Lab color: {lab_color}")

    # Convert Lab back to XYZ
    xyz_back = lab_converter.lab_to_XYZ(lab_color)
    print(f"Converted back to XYZ: {xyz_back}")

    # Convert Lab to LCH
    lch_color = lab_converter.lab_to_lch(lab_color)
    print(f"LCH color: {lch_color}")

    # Convert LCH back to Lab
    lab_back = lab_converter.lch_to_lab(lch_color)
    print(f"Converted back to Lab: {lab_back}")

    # Convert XYZ to xyY
    xyY_color = lab_converter.XYZ_to_xyY(xyz_color)
    print(f"xyY color: {xyY_color}")

    # Convert xyY back to XYZ
    xyz_back_xyY = lab_converter.xyY_to_XYZ(xyY_color)
    print(f"Converted back to XYZ from xyY: {xyz_back_xyY}")


def luvColorConverter_use():
    # Create an instance of LuvColorConverter with D65 reference white
    luv_converter = LuvColorConverter(reference_white='D65')
    # luv_converter = LuvColorConverter(reference_white=[95.047, 100.0, 108.883]) #可以直接指定参考白

    # Define an XYZ color
    xyz_color = np.array([100, 100.0, 100])

    # Convert XYZ to Luv
    luv_color = luv_converter.XYZ_to_luv(xyz_color)
    print(f"Luv color: {luv_color}")

    # Convert Luv back to XYZ
    xyz_back = luv_converter.luv_to_XYZ(luv_color)
    print(f"Converted back to XYZ: {xyz_back}")

    # Convert Luv to LCH
    lch_color = luv_converter.luv_to_lch(luv_color)
    print(f"LCH color: {lch_color}")

    # Convert LCH back to Luv
    luv_back = luv_converter.lch_to_luv(lch_color)
    print(f"Converted back to Luv: {luv_back}")

    # Convert Luv to LsH
    lsh_color = luv_converter.luv_to_lsh(luv_color)
    print(f"LsH color: {lsh_color}")

    # Convert LsH back to Luv
    luv_back_lsh = luv_converter.lsh_to_luv(lsh_color)
    print(f"Converted back to Luv from LsH: {luv_back_lsh}")

    # Convert XYZ to xyY
    xyY_color = luv_converter.XYZ_to_xyY(xyz_color)
    print(f"xyY color: {xyY_color}")

    # Convert xyY back to XYZ
    xyz_back_xyY = luv_converter.xyY_to_XYZ(xyY_color)
    print(f"Converted back to XYZ from xyY: {xyz_back_xyY}")


def lms2006Converter_use():
    # 创建转换器实例
    converter_10 = LMS2006Converter(fov=10)
    converter_2 = LMS2006Converter(fov=2)

    # 进行颜色空间转换
    lms_values = np.array([0.5, 0.3, 0.8])

    # 10° FOV转换
    xyz_10 = converter_10.lms_to_xyz(lms_values)
    lms_back_10 = converter_10.xyz_to_lms(xyz_10)

    # 2° FOV转换
    xyz_2 = converter_2.lms_to_xyz(lms_values)
    lms_back_2 = converter_2.xyz_to_lms(xyz_2)



# sRGB到XYZ转换矩阵
sRGB_to_XYZ_matrix = np.array([
    [0.4124564, 0.3575761, 0.1804375],
    [0.2126729, 0.7151522, 0.0721750],
    [0.0193339, 0.1191920, 0.9503041]
])


