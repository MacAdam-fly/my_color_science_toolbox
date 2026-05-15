# colour是一个标准数据包，我的目的是比对我自己写的和标准数据包
import colour

# CIECAM02正向计算
XYZ = [19.01, 20.00, 21.78]  # 测试样品
XYZ_w = [95.05, 100.00, 108.88]  # D65白点
L_A = 318.31  # 适应场亮度
Y_b = 20.0  # 背景亮度
surround = colour.VIEWING_CONDITIONS_CIECAM02['Average']

specification = colour.XYZ_to_CIECAM02(XYZ, XYZ_w, L_A, Y_b, surround)
print(f"J: {specification.J}, C: {specification.C}, h: {specification.h}")

# CAM16正向计算
specification_cam16 = colour.XYZ_to_CAM16(XYZ, XYZ_w, L_A, Y_b, surround)
print(f"J: {specification_cam16.J}, C: {specification_cam16.C}, h: {specification_cam16.h}")

print(123)