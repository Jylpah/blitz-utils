import logging
import json
from warnings import warn
from typing import Any, Optional, Self
from enum import IntEnum, StrEnum, Enum, EnumType
# from aenum import Enum as AEnum, MultiValue 	# type: ignore
from pydantic import root_validator, validator, Field, Extra

from pyutils import CSVExportable, TXTExportable,  JSONExportable, \
					CSVImportable, TXTImportable, JSONImportable, \
					Idx, BackendIndexType, BackendIndex
from pyutils.exportable import	DESCENDING, ASCENDING, TEXT

logger = logging.getLogger()
error 	= logger.error
message	= logger.warning
verbose	= logger.info
debug	= logger.debug


# class EnumVehicleType(AEnum):
# 	""""Advanced Enum class to combine EnumVehicleTypeInt and 
# 		EnumVehicleTypeStr. 
# 		use vehicle_type.value to get int value
# 		use vehicle_type.fullname to get str value"""
# 	_init_ = 'value fullname'
# 	_settings_ = MultiValue
	
# 	light_tank		= 0, 'lightTank'
# 	medium_tank		= 1, 'mediumTank'
# 	heavy_tank		= 2, 'heavyTank'
# 	tank_destroyer	= 3, 'AT-SPG'

# 	def __str__(self) -> str:
# 		return f'{self.name}'.replace('_', ' ').capitalize()

# #* mypy raises error: 
## "Type[EnumVehicleType]" has no attribute "__iter__" (not iterable)  [attr-defined]
# for vt in EnumVehicleType:
# 	print(vt.name)


class EnumVehicleType(int, Enum):
	
	__alias_map__ : dict[str, str] = dict()

	light_tank		= (0, 'lightTank')
	medium_tank		= (1, 'mediumTank')
	heavy_tank		= (2, 'heavyTank')
	tank_destroyer	= (3, 'AT-SPG')

	def __init__(self, *values) -> None:
		self._api_name : str
		self.__alias_map__[self.api_name] = self.name
		self.__alias_map__[self.name] = self.name
		

	@classmethod
	# def __new__(cls, enum_type: type[Self], value: int, api_name: str):
	def __new__(cls, enum_type: type[Self], *values):
		value: int = int(values[0])
		api_name : str = str(values[1])
		obj = int.__new__(cls, value)
		obj._value_ = value
		obj._api_name = api_name
		return obj


	@classmethod
	def _missing_(cls, value: object):
		if isinstance(value, str):
			item_name : str = cls.__alias_map__[value]
			return cls[item_name]
		return super()._missing_(value)


	@property
	def api_name(self) -> str:
		return self._api_name
	

	def __str__(self) -> str:
		return f'{self.name}'.replace('_', ' ').capitalize()



class EnumVehicleTypeInt(IntEnum):
	light_tank 	= 0
	medium_tank = 1
	heavy_tank 	= 2
	tank_destroyer = 3


	@classmethod
	def _missing_(cls, value: object):
		if isinstance(value, EnumVehicleTypeStr):
			return cls[value.name]
		elif isinstance(value, str):
			return cls[EnumVehicleTypeStr(value).name]
		return super()._missing_(value)


	def __str__(self) -> str:
		return f'{self.name}'.replace('_', ' ').capitalize()


	## DEPRECIATED ############################
	def as_str(self) -> 'EnumVehicleTypeStr':
		warn("This method will deprecated; version=0.2.0", 
			DeprecationWarning, stacklevel=2)
		return EnumVehicleTypeStr[self.name]

	## DEPRECIATED ############################
	@property
	def str_type(self) -> 'EnumVehicleTypeStr':
		warn("This method will deprecated; version=0.2.0", 
			DeprecationWarning, stacklevel=2)
		return EnumVehicleTypeStr[self.name]

	## DEPRECIATED ############################
	@classmethod
	def from_str(cls, t: str) -> 'EnumVehicleTypeInt':
		warn("This method will deprecated; version=0.2.0", 
			DeprecationWarning, stacklevel=2)
		return EnumVehicleTypeStr(t).int_type


class EnumVehicleTypeStr(StrEnum):
	light_tank 		= 'lightTank'
	medium_tank 	= 'mediumTank'
	heavy_tank 		= 'heavyTank'
	tank_destroyer	= 'AT-SPG'


	@classmethod
	def _missing_(cls, value: object):
		"""Make possible to """
		if isinstance(value, EnumVehicleTypeInt):
			return cls[value.name]
		elif isinstance(value, int):
			return cls[EnumVehicleTypeInt(value).name]
		return super()._missing_(value)


	def __str__(self) -> str:
		return f'{self.name}'.replace('_', ' ').capitalize()

	## DEPRECIATED ############################
	@property
	def int_type(self) -> 'EnumVehicleTypeInt':
		warn("This method will deprecated; version=0.2.0", 
			DeprecationWarning, stacklevel=2)
		return EnumVehicleTypeInt[self.name]
	
	## DEPRECIATED ############################
	def as_int(self) -> EnumVehicleTypeInt:
		warn("This method will deprecated; version=0.2.0", 
			DeprecationWarning, stacklevel=2)
		return EnumVehicleTypeInt[self.name]

	## DEPRECIATED ############################
	@classmethod
	def from_int(cls, t: int) -> 'EnumVehicleTypeStr':
		warn("This method will deprecated; version=0.2.0", 
			DeprecationWarning, stacklevel=2)
		return EnumVehicleTypeInt(t).str_type


class EnumVehicleTier(IntEnum):
	I 		= 1
	II 		= 2
	III 	= 3
	IV 		= 4
	V 		= 5
	VI 		= 6
	VII 	= 7
	VIII 	= 8
	IX 		= 9
	X		= 10

	def __str__(self) -> str:
		return str(self.name)

	@classmethod
	def read_tier(cls, tier: str) -> 'EnumVehicleTier':
		try:
			if tier.isdigit():
				return EnumVehicleTier(int(tier))
			else:
				return EnumVehicleTier[tier]
		except Exception as err:
			raise ValueError(f"incorrect tier: '{tier}': {err}")


class EnumNation(IntEnum):
	ussr		= 0
	germany		= 1
	usa 		= 2
	china 		= 3
	france		= 4
	uk			= 5
	japan		= 6
	other		= 7
	european	= 8

	def __str__(self) -> str:
		if self.value in [ 0 , 2, 5]:
			return f'{self.name}'.upper()
		else:
			return f'{self.name}'.capitalize()




class WGTank(JSONExportable, JSONImportable):
	#id 			: int 						= Field(default=0, alias = '_id')
	tank_id 	: int 						= Field(default=..., alias = '_id')
	name   		: str | None				= Field(default=None)
	nation   	: EnumNation | None	 		= Field(default=None)
	type 	  	: EnumVehicleTypeStr| None	= Field(default=None)
	tier 		: EnumVehicleTier| None 	= Field(default=None)
	is_premium 	: bool 						= Field(default=False)

	class Config:		
		allow_mutation 			= True
		validate_assignment 	= True
		allow_population_by_field_name = True
		extra 					= Extra.allow


	@property
	def index(self) -> Idx:
		"""return backend index"""
		return self.tank_id


	@property
	def indexes(self) -> dict[str, Idx]:
		"""return backend indexes"""
		return { 'tank_id': self.index }


	@classmethod
	def backend_indexes(cls) -> list[list[tuple[str, BackendIndexType]]]:
		indexes : list[list[BackendIndex]] = list()
		indexes.append([ ('tier', ASCENDING), 
						 ('type', ASCENDING)
						])
		indexes.append([ ('tier', ASCENDING), 
						 ('nation', ASCENDING)
						])
		indexes.append([ ('name', TEXT) 							
						])		
		return indexes


	@validator('tank_id')
	def validate_id(cls, v: int) -> int:
		if v > 0:
			return v
		raise ValueError('id must be > 0')


	# @root_validator(pre=True)
	# def set_tank_id(cls, values: dict[str, Any])  -> dict[str, Any]:
	# 	if 'tank_id' in values:
	# 		values['id'] = values['tank_id']
	# 	elif '_id' in values:
	# 		values['tank_id'] = values['_id']
	# 	elif 'id' in values:
	# 		values['tank_id'] = values['id']
	# 	else:
	# 		raise ValueError("'tank_id' or 'id' is not defined")		
	# 	return values


	# @validator('tier')
	# def validate_tier(cls, v: int) -> int:
	# 	if v > 0 and v <= 10:
	# 		return v
	# 	raise ValueError('tier must be [0 ... 10]')

	# @validator('type')
	# def validate_type(cls, v: str) -> str:
	# 	if v in [ t.value for t in EnumVehicleTypeStr]:
	# 		return v
	# 	raise ValueError(f'Unknown tank type: {v}')


	@validator('nation', pre=True)
	def validate_nation(cls, v: str) -> EnumNation:
		return EnumNation[v]

	
class Tank(JSONExportable, JSONImportable, \
			CSVExportable, CSVImportable, TXTExportable):
	tank_id 	: int						= Field(default=..., alias='_id')
	name 		: str | None				= Field(default=None, alias='n')
	nation		: EnumNation | None 		= Field(default=None, alias='c')
	type		: EnumVehicleType | None	= Field(default=None, alias='v')
	tier		: EnumVehicleTier | None 	= Field(default=None, alias='t')
	is_premium 	: bool 						= Field(default=False, alias='p')
	next_tanks	: list[int] | None			= Field(default=None, alias='s')

	_exclude_defaults = False

	class Config:		
		allow_mutation 			= True
		validate_assignment 	= True
		allow_population_by_field_name = True
		# use_enum_values			= True


	@property
	def index(self) -> Idx:
		"""return backend index"""
		return self.tank_id


	@property
	def indexes(self) -> dict[str, Idx]:
		"""return backend indexes"""
		return { 'tank_id': self.index }


	@classmethod
	def backend_indexes(cls) -> list[list[tuple[str, BackendIndexType]]]:
		indexes : list[list[BackendIndex]] = list()
		indexes.append([ ('tier', ASCENDING), 
						 ('type', ASCENDING)
						])
		indexes.append([ ('tier', ASCENDING), 
						 ('nation', ASCENDING)
						])
		indexes.append([ ('name', TEXT) 							
						])		
		return indexes

	
	@validator('next_tanks', pre=True)
	def next_tanks2list(cls, v):
		try:
			if v is not None:
				return [ int(k) for k in v.keys() ]
		except Exception as err:
			error(f"Error validating 'next_tanks': {err}")
		return None


	# @validator('type', pre=True)
	# def prevalidate_type(cls, v):
	# 	if isinstance(v, int):
	# 		return EnumVehicleTypeStr.from_int(v).value
	# 	else:
	# 		return v


	# @validator('type')
	# def validate_type(cls, v):
	# 	if isinstance(v, str):
	# 		return EnumVehicleTypeInt(v)
	# 	else:
	# 		return v


	@validator('tier', pre=True)
	def prevalidate_tier(cls, v: Any):
		if isinstance(v, str):
			return EnumVehicleTier[v.upper()].value
		else:
			return v
		

	@validator('tier')
	def validate_tier(cls, v):
		if isinstance(v, int):
			return EnumVehicleTier(v)
		else:
			return v


	def __str__(self) -> str:
		return f'{self.name}'


	# @classmethod
	# def from_id(cls, id : int) -> 'Tank':
	# 	return Tank(tank_id=id)


	# @classmethod
	# def transform(cls, in_obj: JSONExportable) -> Optional['Tank']:
	# 	"""Transform object to out_type if supported"""		
	# 	try:
	# 		if isinstance(in_obj, WGTank):
	# 			return cls.transform_WGTank(in_obj)
	# 	except Exception as err:
	# 		error(f'{err}')
	# 	return None

	
	@classmethod
	def transform_WGTank(cls, in_obj: WGTank) -> Optional['Tank']:
		"""Transform WGTank object to Tank"""
		try:
			# debug(f'type={type(in_obj)}')
			# debug(f'in_obj={in_obj}')
			tank_type : EnumVehicleTypeInt | None = None
			if in_obj.type is not None:
				tank_type = EnumVehicleTypeInt[in_obj.type.name]
			return Tank(tank_id=in_obj.tank_id, 
						name=in_obj.name, 
						tier=in_obj.tier, 
						type=tank_type, 
						is_premium=in_obj.is_premium, 
						nation=in_obj.nation,
						)			
		except Exception as err:
			error(f'{err}')
		return None


	def csv_headers(self) -> list[str]:
		"""Provide CSV headers as list"""
		return list(Tank.__fields__.keys())


	def csv_row(self) -> dict[str, str | int | float | bool]:
		"""Provide CSV row as a dict for csv.DictWriter"""
		if (res:= json.loads(self.json_src())) is not None:
			return self.clear_None(res)
		raise ValueError(f'Could not create CSV row for {self}')


	def txt_row(self, format : str = '') -> str:
		"""export data as single row of text"""
		return f'({self.tank_id}) {self.name} tier {self.tier} {self.type} {self.nation}'
		

Tank.register_transformation(WGTank, Tank.transform_WGTank)
