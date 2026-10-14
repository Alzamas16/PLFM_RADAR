"""Export bilingual text cells without writing to source workbooks."""
import csv
import hashlib
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
OUT = ROOT / 'docs/zh-CN/tables'
OUT.mkdir(parents=True, exist_ok=True)
books = json.loads((ROOT / '5_Simulations/generated/project_review_20261008/workbook_extract.json').read_text(encoding='utf-8'))

PAIRS = {
 'BOARD':'电路板', 'COMPONENT':'组件', 'PART NUMBER':'器件型号', 'N°':'编号',
 'VOLTAGE PINS':'电源引脚', 'RATING (V)':'额定电压范围（V）', 'CURRENT (mA)':'电流（mA）',
 'SELECTED VOLTAGE (V)':'选定电压（V）', 'VOLTAGE RAIL':'电源轨',
 'VOLTAGE RAIL AFTER BRANCHING AND FILTERING':'分支及滤波后的电源轨',
 'ENABLE V':'电压使能', 'SEQUENCE':'时序', 'YES':'是', 'NO':'否',
 'CLOCKS & FREQUENCY SYNTHESIZER BOARD':'时钟与频率合成板', 'CLOCK SYNTHESIZER':'时钟合成器',
 'MICROWAVE POWER AMPLIFIER BOARD':'微波功率放大器板', 'MAIN BOARD':'主板',
 'MISCELLANEOUS':'其他组件', 'RF FRONT END':'射频前端', 'RF POWER AMPLIFIER':'射频功率放大器',
 'CURRENT SENSOR PA':'功放电流检测器', 'ADC PA & T°C Sensor':'功放及温度传感器 ADC',
 'DAC PA':'功放控制 DAC', 'OPAMP PA':'功放运算放大器', 'OPAMP':'运算放大器',
 'PHASER':'移相器', 'Mixer':'混频器', 'MICROCONTROLLER':'微控制器', 'RF SWITCH':'射频开关',
 'Barometer':'气压计', 'STEPPER MOTOR DRIVER':'步进电机驱动器', 'COOLING SYSTEM':'冷却系统',
 'Temperature Sensor':'温度传感器', 'TX Power_up':'发射链上电', 'TX Power_down':'发射链断电',
 'RX Power-up':'接收链上电', 'RX Power_down':'接收链断电',
 'Bias-up Procedure':'偏置上电步骤', 'Bias-Down Procedure':'偏置断电步骤',
 'Apply when temperature reaches a threshold (Relay)':'温度达到阈值时接通（继电器）',
 'Apply RF signal':'施加射频信号', 'Turn off RF signal':'关闭射频信号',
 'Set ID limit to 2840 mA, IG limit to 10 mA':'将 ID 限值设为 2840 mA，IG 限值设为 10 mA',
 'Set VG to −4.0 V':'将 VG 设为 −4.0 V', 'Set VD +22 V':'将 VD 设为 +22 V',
 'Adjust VG more positive until IDQ = 1680 mA':'将 VG 向更正的方向调整，直至 IDQ = 1680 mA',
 'Reduce VG to −4.0 V. Ensure IDQ ~ 0 mA':'将 VG 降至 −4.0 V，确保 IDQ 约为 0 mA',
 'Set VD to 0 V':'将 VD 设为 0 V', 'Turn off VD supply':'关闭 VD 电源',
 'Turn off VG supply':'关闭 VG 电源',
 'It is recommended to power up the AVDD3 pins (3.3 V) before or at the same time as the AVDD1 pin (−5 V)':'建议 AVDD3 引脚（3.3 V）先于 AVDD1 引脚（−5 V）上电，或同时上电。',
 'bring the 1.8 V supplies high and stable prior to or simultaneously with the 3.3 V supplies. It is recommended to hold the RESET pin low while both supply domains settle to ensure that the 3.3 V supplies do not lead the 1.8 V supplies':'使 1.8 V 电源先于 3.3 V 电源达到稳定高电平，或同时达到稳定高电平。建议在两个电源域稳定期间保持 RESET 引脚为低电平，确保 3.3 V 电源不会先于 1.8 V 电源上电。',
 'Parts':'器件位号集合', 'Qty':'数量', 'Value':'标称值', 'Device':'器件',
 'Package':'封装', 'Description':'说明', 'DESCRIPTION':'说明', 'Designator':'位号',
 'DESIGNATOR':'位号', 'MANUFACTURER_PART_NUMBER':'制造商器件型号',
 'MANUFACTURER_NAME':'制造商名称', 'MFR_NAME':'制造商名称', 'Manufacturer':'制造商',
 'MPN':'制造商器件型号', 'NOTE':'备注', 'REMARKS':'备注', 'RefDes':'参考位号', 'REFDES':'参考位号',
 'Layer':'层', 'Top':'顶层', 'Rotation':'旋转角度', 'Rotation °':'旋转角度（°）',
 'Mid X (mm)':'中心 X 坐标（mm）', 'Mid Y (mm)':'中心 Y 坐标（mm）',
 'Mid_X(mm)':'中心 X 坐标（mm）', 'Mid_Y(mm)':'中心 Y 坐标（mm）',
 'MidX mm':'中心 X 坐标（mm）', 'MidY mm':'中心 Y 坐标（mm）',
 'CAPACITOR, European symbol':'电容，欧洲制图符号', 'INDUCTOR, European symbol':'电感，欧洲制图符号',
 'INDUCTOR, American symbol':'电感，美国制图符号', 'RESISTOR, European symbol':'电阻，欧洲制图符号',
 'CONNECTOR':'连接器', 'PIN HEADER':'排针', 'POWER_INDUCTOR':'功率电感',
 'Blue':'蓝色', 'Blue SMD LED':'蓝色贴片 LED', 'Green':'绿色', 'Green SMD LED':'绿色贴片 LED',
 'MINI USB-B Conector':'Mini USB-B 连接器', 'SMD solder JUMPER':'贴片焊接跳线',
 '12.0MHz Crystal':'12.0MHz 晶体', 'EMIFIL (R) Chip Ferrite Bead for GHz Noise':'EMIFIL（R）芯片铁氧体磁珠，用于 GHz 噪声抑制',
 'Momentary Switch (Pushbutton) - SPST':'瞬时按键开关，单刀单掷（SPST）',
 'SMA Connector Jack, Female Socket 50 Ohms Through Hole Solder':'SMA 母座连接器，50 Ω，通孔焊接',
 'Conn Twinax F 0Hz to 4GHz 100Ohm Solder ST Thru-Hole Gold':'Twinax 母连接器，0 Hz 至 4 GHz，100 Ω，直式通孔焊接，镀金',
 '.100 (2.54mm) Center Header - 2 Pin"':'中心间距 0.100 英寸（2.54 mm）的排针，2 针',
 '.100 (2.54mm) Center Header - 3 Pin"':'中心间距 0.100 英寸（2.54 mm）的排针，3 针',
 'Three-wire Automotive Temperature Serial EEPROM 1K (64 x 16)':'三线串行 EEPROM，汽车温度范围，1K（64×16）',
 'Artix-7 Field Programmable Gate Array (FPGA) IC 170 2764800 52160 256-LBGA Check availability':'Artix-7 FPGA 芯片；原描述参数 170、2764800、52160；256-LBGA 封装；请核查供货情况',
 'RF Amplifier':'射频放大器', 'Shunt Resistor':'分流电阻', 'unknown':'未知',
 'Do Not Put':'不要贴装', 'Not a component':'不是元器件', 'Okay, Please proceed':'可以，请继续',
 'information on chip will be removed':'芯片上的标识信息将被去除',
 '[DNP不要贴];':'[DNP：不要贴装]；', '[Supplied by customer客供];':'[由客户提供，客供]；',
 '[Price is changing higher, final price should be subjected to the real price when order!]':'[价格正在上涨，最终价格以订购时的实际价格为准！]',
 'The part we can get here was made in the year of 2022+ OK？':'此处可供应器件生产年份为 2022 年及以后，可以接受吗？',
 'The quoted part number is [NX3215SA-32.768K-STD-MUS-2], not [NX3225GD-8MHZ-STD-CRA-3/XTAL] as specified in description':'报价型号为 [NX3215SA-32.768K-STD-MUS-2]，不是描述中所写的 [NX3225GD-8MHZ-STD-CRA-3/XTAL]。',
 'The quoted part number is [NX3225GD-8MHZ-STD-CRA-3], not [XTAL] as specified in description,The correct package for the listed Part Number [NX3225GD-8MHZ-STD-CRA-3] is indeed [SMD3225-2P], not [3225].Please confirm.':'报价型号为 [NX3225GD-8MHZ-STD-CRA-3]，不是描述中的 [XTAL]。型号 [NX3225GD-8MHZ-STD-CRA-3] 的正确封装确为 [SMD3225-2P]，不是 [3225]，请确认。',
 'AD9523BCPZ, PLL Clock Driver Dual, 72-Pin LFCSP VQ':'AD9523BCPZ，双 PLL 时钟驱动器，72 引脚 LFCSP VQ 封装',
 '800 mA Ultralow Noise, High PSRR, RF Linear Regulator':'800 mA 超低噪声、高电源抑制比射频线性稳压器',
 '4.5 V to 17 V input, 2 A output, synchronous step-down converter in FCCM mode 6-SOT-23-THIN -40 to 125':'输入 4.5 V 至 17 V、输出 2 A 的同步降压转换器，FCCM 模式，6-SOT-23-THIN 封装，温度范围 -40 至 125（原单元格未列单位）',
 '2-A, low-VIN, low-2-A, low-VIN, low-noise, ultra-low-dropout voltage regulator with power good wi 20-VQFN -40 to 125':'2 A、低输入电压、低噪声、超低压差稳压器，带电源良好指示，20-VQFN 封装，温度范围 -40 至 125；原文 low-2-A/low-VIN 重复，wi 截断',
 'T521, Tantalum, Polymer Tantalum, Commercial Grade, 47 uF, 20%, 20 VDC, 105C, -55C, 105C, SMD, Polymer, Molded, Low Profile/ESR, NonCombustible, 2,000 Hrs, 9 % , 45 mOhms, 94 uA, 222.95 mg, 7343, 1.4mm, Height Max = 1.5mm, 1000, 52 Weeks':'T521，钽电容、聚合物钽、商业级，47 uF、20%、20 VDC、105C、-55C、105C，贴片、聚合物、模塑、低外形/低 ESR、不燃，2,000 小时、9 %、45 mOhms、94 uA、222.95 mg、7343、1.4mm，最大高度 1.5mm，1000、52 周；各参数顺序与数值按原文保留，末尾 1000 的含义未注明',
 '*Mfg Part #':'*制造商器件型号', '*Designator':'*位号', '*Package/Footprint':'*封装/焊盘',
 '*Qty':'*数量', 'Description / Value':'说明/标称值', 'HEIGHT':'高度', 'Item #':'项目编号',
 'MOUSER_PART_NUMBER':'Mouser 器件编号', 'MOUSER_PRICE-STOCK':'Mouser 价格/库存',
 'OC_FARNELL':'Farnell 订货代码', 'OC_NEWARK':'Newark 订货代码', 'POPULARITY':'受欢迎程度',
 'SPICEPREFIX':'SPICE 前缀', 'TYPE':'类型', 'Type':'类型', 'Your Instructions / Notes':'你的说明/备注',
}

def norm(s):
    return re.sub(r'\s+', ' ', s).strip()

def translate(s):
    n = norm(s)
    if n in PAIRS:
        return PAIRS[n], '已翻译'
    match = re.fullmatch(r'(\d+)\. (.+)', n)
    if match:
        k, body = match.groups()
        m = re.fullmatch(r'Set the (\S+) pin to (.+)\.', body)
        if m:
            return f'{k}. 将 {m[1]} 引脚设为 {m[2]}。', '已翻译'
        m = re.fullmatch(r'Apply the RF signal to the (\S+) pin\.', body)
        if m:
            return f'{k}. 向 {m[1]} 引脚施加射频信号。', '已翻译'
        m = re.fullmatch(r'Decrease the (\S+) voltage to (.+)\.', body)
        if m:
            return f'{k}. 将 {m[1]} 电压降低到 {m[2]}。', '已翻译'
        special = {'Connect all GND pins to ground.':'将所有 GND 引脚接地。',
                   'Turn off the RF signal.':'关闭射频信号。',
                   'Increase the VGG_PA voltage to achieve the desired IDQ_PA.':'提高 VGG_PA 电压，达到所需 IDQ_PA。'}
        if body in special:
            return k+'. '+special[body], '已翻译'
    m = re.fullmatch(r'The correct (capacitance|inductance|resistance) value for the listed Part Number (.+) is indeed (.+), not (.+)\.Please confirm\.', n)
    if m:
        kind = {'capacitance':'电容', 'inductance':'电感', 'resistance':'电阻'}[m[1]]
        return f'所列型号 {m[2]} 的正确{kind}值确为 {m[3]}，不是 {m[4]}，请确认。', '已翻译'
    m = re.fullmatch(r'The correct package for the listed Part Number (.+) is indeed (.+), not (.+)\.Please confirm\.', n)
    if m:
        return f'所列型号 {m[1]} 的正确封装确为 {m[2]}，不是 {m[3]}，请确认。', '已翻译'
    m = re.fullmatch(r'The part we will supply is (.+?)\s*OK？', n)
    if m:
        return f'将供应的器件型号为 {m[1]}，可以接受吗？', '已翻译'
    if re.search(r'[a-z]{3}', n) and ' ' in n and not n.startswith('http'):
        brands = {'Keystone Electronics', 'Analog Devices Inc', 'Texas Instruments'}
        if n not in brands:
            return s, '待人工核对'
    return s, '型号/位号/数值/名称按原文保留'

pending = []
index = ['# Excel 表格中文对照', '',
         '覆盖全部 13 个原工作簿中的非公式文本单元格。每行列出工作表、单元格、原文、中文及处理状态。数值、公式、器件型号、位号、电源网名与厂商品牌原样保留；本轮不改制造输入，也不改写原工作簿。完整数值与公式仍以源表为准。', '',
         '电源时序和采购问答只忠实翻译，不代表已在硬件上验证，采购价格和答复只代表源文件记录。', '',
         '| 工作簿 | 文本单元格数 | 中文对照 |', '|---|---:|---|']
for book in books:
    p = Path(book['path'])
    folder = p.parent.name
    name = folder+'__'+p.stem+'.csv'
    rows = []
    for sheet in book['sheets']:
        for c in sheet['texts']:
            zh, status = translate(c['text'])
            rows.append({'sheet':sheet['name'], 'cell':c['cell'], 'original':c['text'], '中文':zh, '状态':status})
            if status == '待人工核对':
                pending.append({'path':book['path'], **rows[-1]})
    with (OUT/name).open('w', encoding='utf-8-sig', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=['sheet','cell','original','中文','状态'])
        writer.writeheader()
        writer.writerows(rows)
    source_hash = hashlib.sha256((ROOT/book['path']).read_bytes()).hexdigest()
    index.append(f'| `{book["path"]}` | {len(rows)} | [{p.stem}](tables/{name.replace(" ", "%20")}) |')
    index.extend(['', f'源 SHA256（{p.name}）：`{source_hash}`。', ''])
(ROOT / 'docs/zh-CN/表格中文对照.md').write_text('\n'.join(index), encoding='utf-8')
(ROOT / '5_Simulations/generated/project_review_20261008/workbook_pending.json').write_text(json.dumps(pending, ensure_ascii=False, indent=2), encoding='utf-8')
print(json.dumps({'workbooks':len(books), 'pending':pending}, ensure_ascii=False, indent=2))
