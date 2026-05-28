# Gamut utilities migrated into color_agent/utils
import numpy as np
import matplotlib.pyplot as plt
import matplotlib
from shapely.geometry import Polygon
matplotlib.use('TkAgg')

class GamutInfo:
    def __init__(self, LCH_gamut_path):
        self.C_max = np.load(LCH_gamut_path)
        self.LCH_gamut = self.C_max2LCH_gamut()
        self.Lab_gamut = self.LCH_gamut2Lab_gamut(self.LCH_gamut)
        self.XYZ_gamut = self.Lab_gamut2XYZ_gamut()

    def get_gamut_boarder(self, L, H):
        L_min = int(L)
        L_max = L_min + 1
        H_min = int(H)
        H_max = H_min + 1
        LCH_1 = self.C_max[L_min, H_min]
        LCH_2 = self.C_max[L_max, H_min]
        LCH_3 = self.C_max[L_min, H_max]
        LCH_4 = self.C_max[L_max, H_max]

        L_frac = L - L_min
        H_frac = H - H_min

        C_max = (LCH_1 * (1 - L_frac) * (1 - H_frac) +
                 LCH_2 * L_frac * (1 - H_frac) +
                 LCH_3 * (1 - L_frac) * H_frac +
                 LCH_4 * L_frac * H_frac)

        return C_max

    def C_max2LCH_gamut(self):
        C = np.copy(self.C_max)
        L_range = np.linspace(0, 100, 101, dtype=int)
        H_range = np.linspace(0, 360, 361, dtype=int)

        L = np.tile(L_range, (361, 1)).T
        H = np.tile(H_range, (101, 1))

        LCH_gamut = np.zeros((101, 361, 3))

        LCH_gamut[:, : ,0] = L
        LCH_gamut[:, :, 1] = C
        LCH_gamut[:, :, 2] = H

        return LCH_gamut

    def C_max2Lab_gamut(self):
        C_gamut = np.copy(self.C_max)
        L_range = np.linspace(0, 100, 101, dtype=int)
        H_range = np.linspace(0, 360, 361, dtype=int)

        L = np.tile(L_range, (361, 1)).T
        H = np.tile(H_range, (101, 1))

        a = C_gamut * np.cos(H / 180 * np.pi)
        b = C_gamut * np.sin(H / 180 * np.pi)

        Lab_gamut = np.zeros((101, 361, 3))

        Lab_gamut[:, :, 0] = L
        Lab_gamut[:, :, 1] = a
        Lab_gamut[:, :, 2] = b

        return Lab_gamut

    def LCH_gamut2Lab_gamut(self, LCH_gamut):
        LCH_gamut = LCH_gamut.reshape(101, 361, 3)

        L = LCH_gamut[:, :, 0]
        H = LCH_gamut[:, :, 2]

        C_gamut = LCH_gamut[:, :, 1]

        a = C_gamut * np.cos(H / 180 * np.pi)
        b = C_gamut * np.sin(H / 180 * np.pi)

        Lab_gamut = np.zeros((101, 361, 3))

        Lab_gamut[:, :, 0] = L
        Lab_gamut[:, :, 1] = a
        Lab_gamut[:, :, 2] = b

        return Lab_gamut

    def Lab_gamut2XYZ_gamut(self, White_point_XYZ = None):
        if White_point_XYZ is None:
            White_point_XYZ = np.array([95.047, 100.000, 108.883])

        Lab_gamut = self.Lab_gamut.reshape(-1, 3)
        L = Lab_gamut[:, 0]
        a = Lab_gamut[:, 1]
        b = Lab_gamut[:, 2]

        fy = (L + 16) / 116
        fx = a / 500 + fy
        fz = fy - b / 200
        X = np.where(fx > 6 / 29, fx ** 3, (fx - 16 / 116) * 3 * (6 / 29) ** 2) * White_point_XYZ[0]
        Y = np.where(fy > 6 / 29, fy ** 3, (fy - 16 / 116) * 3 * (6 / 29) ** 2) * White_point_XYZ[1]
        Z = np.where(fz > 6 / 29, fz ** 3, (fz - 16 / 116) * 3 * (6 / 29) ** 2) * White_point_XYZ[2]
        XYZ = np.stack([X, Y, Z], axis=-1)

        XYZ_gamut = XYZ.reshape(101, 361, 3)

        return XYZ_gamut

    def XYZ_gamut2Lab_gamut(self, White_point_XYZ = None, XYZ_gamut = None):
        if White_point_XYZ is None:
            White_point_XYZ = np.array([95.047, 100.000, 108.883])

        XYZ_gamut = XYZ_gamut.reshape(-1, 3)
        X = XYZ_gamut[:, 0]
        Y = XYZ_gamut[:, 1]
        Z = XYZ_gamut[:, 2]

        Xr = X / White_point_XYZ[0]
        Yr = Y / White_point_XYZ[1]
        Zr = Z / White_point_XYZ[2]
        fx = np.where(Xr > 0.008856, Xr ** (1 / 3), 7.787 * Xr + 16 / 116)
        fy = np.where(Yr > 0.008856, Yr ** (1 / 3), 7.787 * Yr + 16 / 116)
        fz = np.where(Zr > 0.008856, Zr ** (1 / 3), 7.787 * Zr + 16 / 116)
        L = 116 * fy - 16
        a = 500 * (fx - fy)
        b = 200 * (fy - fz)
        Lab = np.stack([L, a, b], axis=-1)
        Lab_gamut = Lab.reshape(101, 361, 3)

        return Lab_gamut

    def Lab_gamut2LCH_gamut(self, Lab_gamut = None):
        L = Lab_gamut[:, :, 0]
        a = Lab_gamut[:, :, 1]
        b = Lab_gamut[:, :, 2]
        C = np.sqrt(a ** 2 + b ** 2)
        H = np.arctan2(b, a) * 180 / np.pi
        H = np.where(H < 0, H + 360, H)
        LCH_gamut = np.zeros_like(self.Lab_gamut)
        LCH_gamut[:, :, 0] = L
        LCH_gamut[:, :, 1] = C
        LCH_gamut[:, :, 2] = H

        return LCH_gamut

    def calculate_gamut_area(self, L):
        a = self.Lab_gamut[L, :, 1].flatten()
        b = self.Lab_gamut[L, :, 2].flatten()
        points = np.vstack((a, b)).T
        polygon = Polygon(points)
        return polygon.area

    def calculate_gamut_volume(self):
        volume = 0
        for L in range(101):
            area = self.calculate_gamut_area(L)
            volume += area
        return volume

    def compute_gamut_rings(self, L_steps=None):
        if L_steps is None:
            L_steps = [10, 20, 30, 40, 50, 60, 70, 80, 90, 100]

        H_range = np.linspace(0, 360, 361)

        C_prime = np.zeros((101, 361))

        for L in range(101):
            for h_idx, h in enumerate(H_range):
                C_current = self.LCH_gamut[L, h_idx, 1]
                A_Lh = np.pi * (C_current ** 2) / 360
                C_prime[L, h_idx] = np.sqrt(360 * A_Lh / np.pi)

        C_rss = np.zeros((101, 361))

        for h_idx in range(361):
            for L in range(101):
                if L == 0:
                    C_rss[L, h_idx] = C_prime[L, h_idx]
                else:
                    sum_squares = np.sum(C_prime[:L + 1, h_idx] ** 2)
                    C_rss[L, h_idx] = np.sqrt(sum_squares)

        gamut_rings = []

        for L in L_steps:
            L_idx = int(L)
            a_rss = np.zeros(361)
            b_rss = np.zeros(361)

            for h_idx, h in enumerate(H_range):
                C_val = C_rss[L_idx, h_idx]
                h_rad = np.radians(h)
                a_rss[h_idx] = C_val * np.cos(h_rad)
                b_rss[h_idx] = C_val * np.sin(h_rad)

            gamut_rings.append(np.column_stack([a_rss, b_rss]))

        return np.array(gamut_rings), L_steps

    def calculate_gamut_ring_area(self, ring_points):
        x = ring_points[:, 0]
        y = ring_points[:, 1]
        area = 0.5 * np.abs(np.dot(x, np.roll(y, 1)) - np.dot(y, np.roll(x, 1)))
        return area

    def calculate_gamut_rings_areas(self, L_steps=None):
        if L_steps is None:
            L_steps = [10, 20, 30, 40, 50, 60, 70, 80, 90, 100]

        gamut_rings, L_steps_used = self.compute_gamut_rings(L_steps)
        areas = {}

        for ring, L_val in zip(gamut_rings, L_steps_used):
            area = self.calculate_gamut_ring_area(ring)
            areas[L_val] = area

        return areas

    def calculate_gamut_ring_volume(self):
        outer_ring, _ = self.compute_gamut_rings([100])
        volume = self.calculate_gamut_ring_area(outer_ring[0])
        return volume

    def plot_gamut_rings(self, L_steps=None, ax=None, color_map='viridis', label=None):
        if ax is None:
            fig, ax = plt.subplots(figsize=(10, 10))

        gamut_rings, L_steps_used = self.compute_gamut_rings(L_steps)

        colors = plt.cm.get_cmap(color_map, len(L_steps_used))

        for i, (ring, L_val) in enumerate(zip(gamut_rings, L_steps_used)):
            color = colors(i)
            a_vals = ring[:, 0]
            b_vals = ring[:, 1]

            if label and i == 0:
                ax.plot(a_vals, b_vals, color=color, linewidth=2,
                        label=f'{label} (L*={L_val})')
            else:
                ax.plot(a_vals, b_vals, color=color, linewidth=2,
                        label=f'L*={L_val}')

        ax.set_xlabel("a'", fontsize=14)
        ax.set_ylabel("b'", fontsize=14)
        ax.grid(True, alpha=0.3)
        ax.axis('equal')

        if label or len(L_steps_used) > 1:
            ax.legend()

        return ax
