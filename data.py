import copy

# ----------------------------------------------------------------------------------------------------------------------
"""

	DATA.PY
	Static info

"""
# ----------------------------------------------------------------------------------------------------------------------


class Colours:

	_colourRGB = {
		"yellow":		[1.0, 	1.0, 	0.0],
		"green":		[0.0, 	1.0, 	0.0],
		"blue":			[0.0, 	0.0, 	1.0],
		"dark-blue":	[0.0,	0.001,	0.117],
		"red":			[1.0, 	0.0, 	0.0],
		"orange":		[1.0, 	0.17, 	0.0],
		"pale-orange":	[1.0, 	0.25, 	0.1],
		"grey-blue":	[0.03,	0.03,	0.06],
		"grey":			[0.038, 0.038, 	0.038],
		"white":		[1.0,	1.0,	1.0],
		"purple":		[0.25,	0.0,	0.80],
	}

	@staticmethod
	def get_rgb_value(colour):
		"""
		Used to look up rgb colour in _colourRGB dictionary

		:param colour: string name of colour
		:return: rgb 0-1 of colour
		"""
		for item in Colours._colourRGB:
			if item == colour:
				return Colours._colourRGB[item]
		raise ValueError('%s is not an available colour!' % colour)
	# end def get_rgb_value():

	@staticmethod
	def get_linear_value(colour):
		"""
		Look up rgb colour in _colourRGB dictionary and convert to linear colour space

		:param colour: string name of colour
		:return: rgb 0-1 of colour converted to linear space
		"""
		rgb_colour = copy.copy(Colours.get_rgb_value(colour))
		for index, clr in enumerate(rgb_colour):
			shifted_value = (1.055 * (clr ** (1.0 / 2.4)) - 0.055)
			if 0 > shifted_value:
				rgb_colour[ index ] = 0.0
			elif 1 < shifted_value:
				rgb_colour[ index ] = 1.0
			else:
				rgb_colour[ index ] = shifted_value
		return rgb_colour
	# end def get_linear_value():

	@staticmethod
	def list():
		print('Available colours are:')
		for key in Colours._colourRGB:
			print key
	# end def list():
# end class Colours:


controllerShapes = {
	'locator':	[
		[0.0, 0.0, 10.0], [0.0, 0.0, -10.0],
		[0.0, 0.0, 0.0], [10.0, 0.0, 0.0],
		[-10.0, 0.0, 0.0], [0.0, 0.0, 0.0],
		[0.0, 10.0, 0.0], [0.0, -10.0, 0.0]
	],
	'square': [
		[0.0, -5.0, 5.0],
		[0.0, -5.0, -5.0],
		[0.0, 5.0, -5.0],
		[0.0, 5.0, 5.0],
		[0.0, -5.0, 5.0],
	],
	'cube': [
		[-5.0, 5.0, 5.0],
		[-5.0, 5.0, -5.0],
		[5.0, 5.0, -5.0],
		[5.0, 5.0, 5.0],
		[-5.0, 5.0, 5.0],
		[-5.0, -5.0, 5.0],
		[-5.0, -5.0, -5.0],
		[-5.0, 5.0, -5.0],
		[-5.0, 5.0, 5.0],
		[-5.0, -5.0, 5.0],
		[5.0, -5.0, 5.0],
		[5.0, 5.0, 5.0],
		[5.0, 5.0, -5.0],
		[5.0, -5.0, -5.0],
		[5.0, -5.0, 5.0],
		[5.0, -5.0, -5.0],
		[-5.0, -5.0, -5.0],
	],
	'circle': [
		[1.8676216406393552e-32, 4.981122076295701, -3.050057603448874e-16],
		[1.6662388829734572e-32, 4.890486892543706, 0.9727783378718896],
		[-1.317510869535488e-16, 4.601956548308842, 1.9061928061683913],
		[-1.6552905483779703e-16, 4.145954687274185, 2.770238359548337],
		[-2.1670598206161923e-16, 3.5221850343499774, 3.5221850324945163],
		[-2.5358441773023326e-16, 2.770238361131354, 4.145954693904184],
		[-2.818597469983201e-16, 1.9061928036196074, 4.601956518670172],
		[-2.994365504978893e-16, 0.9727783498970166, 4.890487008642385],
		[-3.050106444567172e-16, 9.666633982735322e-12, 4.981121841880426],
		[-2.9945462715433256e-16, -0.9727783471257424, 4.890487008645621],
		[-2.8178890311742663e-16, -1.9061928034785158, 4.601956518657502],
		[-2.5386641533439466e-16, -2.7702383588758273, 4.145954693954642],
		[-2.156716544886982e-16, -3.5221850323094097, 3.522185032309463],
		[-1.6962817071515942e-16, -4.145954692548569, 2.7702383602817524],
		[-1.1672064735578963e-16, -4.601956518657434, 1.9061928034791868],
		[-5.956549413489003e-17, -4.890487007239765, 0.9727783485292154],
		[-1.811213560447317e-31, -4.981121841879551, 2.8663339968228965e-15],
		[5.956549413488921e-17, -4.890487007239767, -0.9727783485292015],
		[1.1672064735578928e-16, -4.6019565186574365, -1.9061928034791822],
		[1.6962817071515863e-16, -4.145954692548577, -2.770238360281738],
		[2.1567165448869784e-16, -3.5221850323094115, -3.5221850323094577],
		[2.5386641533439456e-16, -2.770238358875835, -4.145954693954639],
		[2.8178890311742604e-16, -1.9061928034785178, -4.6019565186574924],
		[2.9945462715433276e-16, -0.9727783471257543, -4.890487008645624],
		[3.0501064445671665e-16, 9.662593451303378e-12, -4.981121841880419],
		[2.9943655049788953e-16, 0.9727783498970054, -4.89048700864239],
		[2.818597469983201e-16, 1.9061928036196039, -4.601956518670168],
		[2.5358441773023356e-16, 2.770238361131345, -4.14595469390419],
		[2.167059820616191e-16, 3.522185034349976, -3.5221850324945136],
		[1.655290548377971e-16, 4.14595468727418, -2.770238359548341],
		[1.3175108695354892e-16, 4.60195654830884, -1.90619280616839],
		[-1.0430361976626458e-31, 4.890486892543704, -0.9727783378718902],
		[-9.984232981597522e-32, 4.9811220762957005, 1.630548985805366e-15]
	],
	'omni-circle': [
		[4.988522487593946, -1.813422251501042e-15, -1.495470492458917e-14],
		[3.9954850484155657, -1.813422251501042e-15, 0.7947512814543433],
		[3.7726285998247686, -1.5484535208531561e-15, 1.562673676070842],
		[3.387208836093357, -1.3509412279125577e-15, 2.263260190801622],
		[2.88744504552709, -1.1032448965502762e-15, 2.8874444464948055],
		[2.263260789119033, -7.848162223856876e-16, 3.387208244867793],
		[1.5626742712309598, -4.628003059463309e-16, 3.77262797672245],
		[0.7947518884645957, -1.0650279066540702e-16, 3.9954845482190406],
		[5.755911124945173e-07, 2.5005114710122665e-16, 4.988521671942211],
		[-0.7947506921336699, 5.875034056030592e-16, 3.995484548222011],
		[-1.562673076383358, 9.249739072571557e-16, 3.772627976710552],
		[-2.263259593250584, 1.1920302329321241e-15, 3.387208244912963],
		[-2.887443848970608, 1.459087696692923e-15, 2.8874444463282187],
		[-3.3872076467284224, 1.615078559450357e-15, 2.263260191434899],
		[-3.772627379352851, 1.7710692828292837e-15, 1.5626736737415423],
		[-3.995483950037586, 1.7922455854001752e-15, 0.7947512903155793],
		[-4.988521096361464, 1.8134216361606375e-15, -1.8873711545211858e-13],
		[-3.995483950037527, 1.6965594137112951e-15, -0.7947512903159255],
		[-3.7726273793527314, 1.5796969481684641e-15, -1.5626736737418658],
		[-3.387207646728224, 1.3425874069719543e-15, -2.263260191435227],
		[-2.8874438489703635, 1.1054776890657688e-15, -2.887444446328496],
		[-2.2632595932502615, 7.842185633152064e-16, -3.387208244913202],
		[-1.5626730763830112, 4.629595618109106e-16, -3.7726279767107296],
		[-0.7947506921332739, 1.0645902949974223e-16, -3.995484548222111],
		[5.755915177511027e-07, -2.5003819704494154e-16, -4.988521671942245],
		[0.7947518884648991, -5.87514718629401e-16, -3.995484548219004],
		[1.5626742712311812, -9.24944692969968e-16, -3.772627976722388],
		[2.263260789119211, -1.1921391758395464e-15, -3.3872082448676966],
		[2.8874450455271994, -1.4586834778603044e-15, -2.8874444464947273],
		[3.3872088360934285, -1.6165927685970495e-15, -2.263260190801543],
		[3.7726285998247944, -1.765408218994902e-15, -1.562673676070801],
		[3.995485048415573, -1.813422251501042e-15, -0.7947512814543308],
		[4.9885224875939445, -1.813422251501042e-15, -1.3009677406004201e-14]
	],
	'winged-arrow': [
		[0.0, 0.0, 0.0],
		[-7.614220773648639, 2.298144716588758, -2.298144716588758],
		[-10.148376747329095, 0.0, 0.0],
		[-7.614220773648639, 2.298144716588758, 2.298144716588758],
		[0.0, 0.0, 0.0],
		[-7.614220773648639, -2.298144716588758, -2.298144716588758],
		[-7.614220773648639, 2.298144716588758, -2.298144716588758],
		[-7.614220773648639, -2.298144716588758, -2.298144716588758],
		[-10.148376747329095, 0.0, 0.0],
		[-7.614220773648639, -2.298144716588758, 2.298144716588758],
		[-7.614220773648639, 2.298144716588758, 2.298144716588758],
		[-7.614220773648639, -2.298144716588758, 2.298144716588758],
		[0.0, 0.0, 0.0]
	]
}