#coding=utf-8

import Image,ImageDraw,ImageFont,os,string,random,ImageFilter,cStringIO,math
from hashlib import md5
import base64


#加密函
def encryption(s='',key=12):
    a = base64.b16encode(s)
    a1=''
    a2=''
    for i in range(len(a)):
        if i%2 == 0:
            a1 = a1+a[i]
        else:
            a2 = a2+a[i]
    b = base64.b16encode(a1+a2)
    b1=''
    b2=''
    for i in range(len(b)):
        if i%2 == 0:
            b1 = b1+b[i]
        else:
            b2 = b2+b[i]
    return b1+b2

def dencryption(s='',key=12):
    a = ''
    for i in range(len(s)/2):
        a = a+ s[i] + s[len(s)/2+i]
    
    b = base64.b16decode(a)
    c=''
    for i in range(len(b)/2):
        c = c+ b[i] + b[len(b)/2+i]
    d = base64.b16decode(c)
    return d

class picChecker(): 
	""" 
	图片验证代码： 
	1) 用户注册需填写图片验证码，以阻止机器人注册 
	2) 图片验证码字符数为 4 位(大小写字母与数字，不区分大小写)。 
	用户如果没有填写验证码或没有填写正确的验证码， 
	页面友好性提示用户填写(同时程序方面也做相应限制) 
	usage: pc = picChecker().createChecker() 
	param: 很多，如下 
		chars 允许的字符集合， 
			类型 list 
			默认值 initChars() 
			例子 ['1','2','3'] 
		length 字符串长度 
			类型 integer 
			默认值 4 
		size 图片大小 
			类型 tutle 
			默认值 (120,30) 
			例子 (120,30) 
		fontsize 字体大小 
			类型 integer 
			默认值 25 
		begin 字符其实位置，即左上角位置 
			类型 tutle 
			默认值 (5,-2) 
		outputType 输出类型 
			类型 string 
			默认值 GIF 
			可选值 GIF JPEG TIFF PNG 
		mode 图片模式 
			类型 string 
			可选值 RGB L (还有其他模式，但只推荐这2种) 
			默认值 RGB 
		backgroundColor 背景色 
		foregroundColor 前景色 
			当mode=RGB时，backgroundColor,foregroundColor为tutle类型 
			取值为(integer,integer,integer) 
			表示RGB颜色值 
			当mode=L时，backgroundColor,foregroundColor为数字，表示黑白模式 
			取值为0-255 
			表示灰度 
		fonttype 字体路径 
			类型 string 
			默认值 "simsum.ttc" 
		jamNum 干扰线条数 
			类型 (int1,int1) 
			int1 干扰线条数下限，包含 
			int2 干扰线条数上线，包含 
		pointBorder 散点噪音 
			构造方法：对每个像素点使用随机函数确定是否在该像素上画散点噪音 
			类型 (int1,int2) 
			int1越大 散点越多 
			int2越大 散点越少 
	return: [picCheckerStr,pic] 
	picCheckerStr: 表示返回图片中对应的字符串,可用于session验证以及其他用途 
	pic : 返回的图片，类型为Image 
	for : 
	todo : Nothing 
	""" 
	def __init__(self, outputType = 'GIF',mode = 'RGB' , 
				backgroundColor = (243,251,254),
				length = 4,jamNum = (1,2), pointBorder = (40,39)): 
		""" 
		初始化配置 
		""" 
		#验证码配置 
		#允许的字符串 
		#self.chars = chars
		#字符大小 
		self.fontsize = 24
		#图片大小
		self.imageL = int(self.fontsize*length*1.5+self.fontsize*1.5)
		self.imageH = self.fontsize*2
		self.size = (self.imageL,self.imageH) 
		#字符起始插入点 
		self.begin = (random.randint(16,26),random.randint(1,8))
		#字符串长度 
		self.length = length 
		#输出类型 
		self.outputType = outputType 

		#图片模式 
		self.mode = mode 
		#背景色 
		self.backgroundColor = backgroundColor 
		#前景色 
		self.foregroundColor = (random.randint(1,120),random.randint(1,120),random.randint(1,120))
		#干扰线条数 
		self.jamNum = jamNum 
		#散点噪音界限 
		self.pointBorder = pointBorder 
		#字体库路径 
                HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
                CAPTCHA_FONT = os.path.join(HERE,'static/Vera.ttf')
		self.fonttype = CAPTCHA_FONT 
		#设置字体,大小默认为18 
		self.font = ImageFont.truetype(self.fonttype, self.fontsize)
	
	def getPicString(self): 
		""" 
		usage: getPicString() 
		return: string 
		for : 生成给定长度的随机字符串 
		todo: Nothing 
		""" 
		#初始化字符串长度 
		length = self.length 
		#初始化字符集合
		string1 = "三 于 干 亏 士 工 土 才 寸 下 大 丈 与 万 上 小 口 巾 山 千 乞 川 亿 个 勺 久 凡 及 夕 丸 么 广 亡 门 义 之 尸 弓 己 已 子 卫 也 女 飞 刃 习 叉 马 乡 丰 王 井 开 夫 天 无 元 专 云 扎 艺 木 五 支 厅 不 太 犬 区 历 尤 友 匹 车 巨 牙 屯 比 互 切 瓦止 少 日 中 冈 贝 内 水 见 午 牛 手 毛 气 升 长 仁 什 片 仆 化 仇 币 仍 仅 斤 爪 反 介 父 从 今凶 分 乏 公 仓 月 氏 勿 欠 风 丹 匀 乌 凤 勾 文 六 方 火 为 斗 忆 订 计 户 认 心 尺 引 丑 巴 孔队 办 以 允 予 劝 双 书 幻"
		chars = string1.split(' ')
		#获得字符集合 
		selectedChars = random.sample(chars,length)
		
		a=''
		for i in range(length):
                        val = random.randint(0x4E00, 0x9FA5)
                        a = a+unichr(val)
                
		#a=a.encode("utf-8")
		
		charsToStr = string.join(selectedChars,'')
		return charsToStr

	def createChecker(self,s=''): 
		""" 
		usage: createChecker() 
		return: [str,pic] 
		str:对应的字符串 
		pic:对应的图片 
		for: 
		todo: 
		""" 
		#获得验证码字符串 
		randStr1 = s
		#将字符串加入空格 
		#randStr1 = string.join([i+" " for i in randStr],"") 
		#创建图形 
		im = Image.new(self.mode,self.size,self.backgroundColor) 
		#创建画笔 
		draw = ImageDraw.Draw(im) 
		#输出随机文本 
		draw.text(self.begin, unicode(randStr1,'UTF-8'), font=self.font,fill=self.foregroundColor)
		
		#im = self.drawText(draw,randStr,im) 
		#干扰线 
		#self.createJam(draw)
		#散点噪音 
		self.createPoints(draw)
		#self.createCurve(draw)
		#图形扭曲
                
		para = [1-float(random.randint(1,2))/100, 
			0, 
			0, 
			0, 
			1-float(random.randint(1,10))/100, 
			float(random.randint(1,2))/500, 
			0.001, 
			float(random.randint(1,2))/500 
			] 
		#print randStr,para 
		im = im.transform(im.size, Image.PERSPECTIVE,para)
                
		#图像滤镜 
		im=im.filter(ImageFilter.EDGE_ENHANCE_MORE)
		
		buf = cStringIO.StringIO()
		im.save(buf, 'gif') 
		
		#im.save("checker.gif",self.outputType)
		#print randStr
		return [randStr1,buf.getvalue()]
		
	def createJam(self,draw): 
		""" 
		usage: 创建干扰线 
		para: draw 表示画笔 
		return: None 
		for: 
		todo: 
		""" 
		#干扰线条数 
		lineNum = random.randint(self.jamNum[0],self.jamNum[1]) 
		for i in range(lineNum): 
			begin = (random.randint(0,self.size[0]),random.randint(0,self.size[1])) 
			end = (random.randint(0,self.size[0]),random.randint(0,self.size[1])) 
			draw.line([begin,end],fill = (0,0,0))
		
	def createPoints(self,draw): 
		""" 
		usage: 创建散点噪音 
		para: draw 表示画笔 
		return: None 
		for: 
		todo: 
		""" 
		#散点噪音 
		for x in range(self.size[0]): 
			for y in range(self.size[1]): 
				flag = random.randint(0,self.pointBorder[0]) 
		if flag > self.pointBorder[1]: 
			draw.point((x,y),fill = (0,0,0)) 
			del flag

                
	def createCurve(self,draw):
                """
                绘干扰线
                正弦型函数解析式：y=Asin(ωx+φ)+b 
                各常数值对函数图像的影响： 
                A：决定峰值（即纵向拉伸压缩的倍数） 
                b：表示波形在Y轴的位置关系或纵向移动距离（上加下减） 
                φ：决定波形与X轴位置关系或横向移动距离（左加右减） 
                ω：决定周期（最小正周期T=2π/∣ω∣）
                """
                a = random.randint(1,self.imageL/2)
                b = random.randint(-self.imageH/4,self.imageH/4)
                f = random.randint(-self.imageH/4,self.imageH/4)
                t = random.randint(self.imageH*1.5,self.imageL*2)
                w = 2*math.pi/t
                px1 = 0
                px2 = random.randint(int(self.imageH/2),int(self.imageL*0.667))
                for i in range(px1,px2):
                        x = i/100
                        y = a*math.sin(w*i+f)+b+self.imageH/2
                        y = math.sin(x)
			m = self.fontsize/4-2
			while m>0:
                                draw.point((x,y),fill = (0,0,0))
                                i-=1    








                
