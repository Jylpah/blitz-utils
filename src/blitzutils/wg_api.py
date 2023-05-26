from typing import Any, Optional, ClassVar, TypeVar
import logging
import pyarrow 							# type: ignore
from bson.objectid import ObjectId
from pydantic import BaseModel, Extra, root_validator, validator, Field, HttpUrl

from pyutils import JSONExportable, JSONImportable, \
					TypeExcludeDict, Idx, BackendIndexType, BackendIndex
from pyutils.utils 		import epoch_now
from pyutils.exportable import	DESCENDING, ASCENDING, TEXT

from .region 	import Region
from .tank 		import Tank

TYPE_CHECKING = True
logger = logging.getLogger()
error 	= logger.error
message	= logger.warning
verbose	= logger.info
debug	= logger.debug


B	= TypeVar('B', bound='BaseModel')


###########################################
# 
# WGApiError()
#
###########################################


class WGApiError(BaseModel):
	code: 	int | None
	message:str | None
	field: 	str | None
	value: 	str | None

	def str(self) -> str:
		return f'code: {self.code} {self.message}'


	
	
###########################################
# 
# WGAccountInfo()
#
###########################################

class WGAccountInfo(JSONExportable):
	account_id 	: int 			= Field(alias='id') 
	region 		: Region | None	= Field(default=None, alias='r')
	created_at 	: int 			= Field(default=0, alias='c')
	updated_at 	: int 			= Field(default=0, alias='u')
	nickname 	: str | None	= Field(default=None, alias='n')
	last_battle_time : int 		= Field(default=0, alias='l')

	# _exclude_export_DB_fields	: ClassVar[Optional[TypeExcludeDict]] = None
	# _exclude_export_src_fields	: ClassVar[Optional[TypeExcludeDict]] = None
	# _include_export_DB_fields	: ClassVar[Optional[TypeExcludeDict]] = None
	# _include_export_src_fields	: ClassVar[Optional[TypeExcludeDict]] = None

	class Config:
		arbitrary_types_allowed = True
		allow_mutation 			= True
		validate_assignment 	= True
		allow_population_by_field_name = True
		extra 					= Extra.allow


	@root_validator()
	def set_region(cls, values: dict[str, Any]) -> dict[str, Any]:
		account_id = values.get('account_id')
		region = values.get('region')
		if isinstance(account_id, int) and region is None:
			values['region'] = Region.from_id(account_id)
		return values


class WGTankStatAll(BaseModel):
	battles			: int = Field(..., alias='b')
	wins 			: int = Field(default=-1, alias='w')
	losses			: int = Field(default=-1, alias='l')
	spotted			: int = Field(default=-1, alias='sp')
	hits			: int = Field(default=-1, alias='h')
	frags			: int = Field(default=-1, alias='k')
	max_xp			: int | None
	capture_points 	: int = Field(default=-1, alias='cp')	
	damage_dealt	: int = Field(default=-1, alias='dd')
	damage_received	: int = Field(default=-1, alias='dr')
	max_frags		: int = Field(default=-1, alias='mk')
	shots			: int = Field(default=-1, alias='sh')
	frags8p			: int | None
	xp				: int | None
	win_and_survived: int = Field(default=-1, alias='ws')
	survived_battles: int = Field(default=-1, alias='sb')
	dropped_capture_points: int = Field(default=-1, alias='dp')

	class Config:		
		allow_mutation 			= True
		validate_assignment 	= True
		allow_population_by_field_name = True


	@validator('frags8p', 'xp', 'max_xp')
	def unset(cls, v: int | bool | None) -> None:
		return None


class WGTankStat(JSONExportable, JSONImportable):
	id					: ObjectId  	= Field(alias='_id')
	region				: Region | None = Field(default=None, alias='r')
	all					: WGTankStatAll = Field(..., alias='s')
	last_battle_time	: int			= Field(..., alias='lb')
	account_id			: int			= Field(..., alias='a')
	tank_id				: int 			= Field(..., alias='t')
	mark_of_mastery		: int 			= Field(default=0, alias='m')
	battle_life_time	: int 			= Field(default=0, alias='l')
	release 			: str  | None 	= Field(default=None, alias='u')
	max_xp				: int  | None
	in_garage_updated	: int  | None
	max_frags			: int  | None
	frags				: int  | None
	in_garage 			: bool | None

	_exclude_export_DB_fields	: ClassVar[Optional[TypeExcludeDict]] = { 	'max_frags': True, 
																			'frags' : True, 
																			'max_xp': True, 
																			'in_garage': True, 
																			'in_garage_updated': True 
																		}
	_exclude_export_src_fields	: ClassVar[Optional[TypeExcludeDict]] = { 'id': True } 
	# _include_export_DB_fields	: ClassVar[Optional[TypeExcludeDict]] = None
	# _include_export_src_fields	: ClassVar[Optional[TypeExcludeDict]] = None

	class Config:
		arbitrary_types_allowed = True
		json_encoders 			= { ObjectId: str }
		allow_mutation 			= True
		validate_assignment 	= True
		allow_population_by_field_name = True


	@property
	def index(self) -> Idx:
		"""return backend index"""
		return self.id


	@property
	def indexes(self) -> dict[str, Idx]:
		"""return backend indexes"""
		return { 	'account_id': self.account_id, 
					'last_battle_time': self.last_battle_time, 
					'tank_id': self.tank_id,
				 }


	@classmethod
	def backend_indexes(cls) -> list[list[tuple[str, BackendIndexType]]]:
		indexes : list[list[BackendIndex]] = list()		
		indexes.append([ 	
						('region', ASCENDING),
						('account_id', ASCENDING),
						('tank_id', ASCENDING),
						('last_battle_time', DESCENDING)
						])
		indexes.append([ 	
						('region', ASCENDING),
						('account_id', ASCENDING),
						('last_battle_time', DESCENDING),
						('tank_id', ASCENDING),
						])					
		indexes.append([
					 	('region', ASCENDING),
						('release', DESCENDING),										
						('tank_id', ASCENDING),
						('account_id', ASCENDING),										
						])
		return indexes


	@classmethod
	def arrow_schema(cls) -> pyarrow.schema:
		return pyarrow.schema([			
			('region', 	pyarrow.dictionary(pyarrow.uint8(), pyarrow.string())),
			('last_battle_time', pyarrow.int64()),
			('account_id', pyarrow.int64()),
			('tank_id' , pyarrow.int32()),
			('mark_of_mastery' , pyarrow.int32()),
			('battle_life_time' , pyarrow.int32()),
			('release', pyarrow.string()),
			('all.spotted' , pyarrow.int32()),
			('all.hits' , pyarrow.int32()),
			('all.frags' , pyarrow.int32()),
			('all.wins' , pyarrow.int32()),
			('all.losses' , pyarrow.int32()),
			('all.capture_points' , pyarrow.int32()),
			('all.battles' , pyarrow.int32()),
			('all.damage_dealt' , pyarrow.int32()),
			('all.damage_received' , pyarrow.int32()),
			('all.max_frags' , pyarrow.int32()),
			('all.shots' , pyarrow.int32()),
			('all.win_and_survived' , pyarrow.int32()),
			('all.survived_battles' , pyarrow.int32()),
			('all.dropped_capture_points' , pyarrow.int32()),
		])


	@classmethod
	def mk_id(cls, 
			  account_id: int, 
			  last_battle_time: int, 
			  tank_id: int = 0
			  ) -> ObjectId:
		return ObjectId(hex(account_id)[2:].zfill(10) + \
						hex(tank_id)[2:].zfill(6) + \
						hex(last_battle_time)[2:].zfill(8)\
						)


	@validator('last_battle_time', pre=True)
	def validate_lbt(cls, v: int) -> int:
		now : int = epoch_now()
		if v > now + 36000:
			return now
		else:
			return v


	@root_validator(pre=True)
	def set_id(cls, values : dict[str, Any]) -> dict[str, Any]:
		try:
			# debug('starting')
			# debug(f'{values}')
			if 'id' not in values and '_id' not in values:
				if 'a' in values:
					values['_id'] = cls.mk_id(values['a'], values['lb'], values['t'])
				else:
					values['id'] = cls.mk_id(values['account_id'], values['last_battle_time'], values['tank_id'])
			return values
		except Exception as err:
			raise ValueError(f'Could not store _id: {err}')

	
	@root_validator(pre=False)
	def set_region(cls, values : dict[str, Any]) -> dict[str, Any]:
		try:
			if 'region' not in values or values['region'] is None:
				values['region'] = Region.from_id(values['account_id'])
			return values
		except Exception as err:
			raise ValueError(f'Could not set region: {err}')



	@validator('max_frags', 'frags', 'max_xp', 'in_garage', 'in_garage_updated')
	def unset(cls, v: int | bool | None) -> None:
		return None


	def __str__(self) -> str:
		return f'account_id={self.account_id}:{self.region} tank_id={self.tank_id} last_battle_time={self.last_battle_time}'


class WGApiWoTBlitz(JSONExportable):
	status	: str	= Field(default="ok", alias='s')
	meta	: dict[str, Any] 	| None	
	error	: WGApiError 		| None

	@validator('error')
	def if_error(cls, v : WGApiError | None) -> WGApiError | None:
		if v is not None:
			error(v.str())
		return v


class WGApiWoTBlitzAccountInfo(WGApiWoTBlitz):	
	data	: dict[str, WGAccountInfo | None ] | None = Field(default=None, alias='d')

	class Config:		
		allow_mutation 			= True
		validate_assignment 	= True
		allow_population_by_field_name = True


class WGApiWoTBlitzTankStats(WGApiWoTBlitz):	
	data	: dict[str, list[WGTankStat] | None ] | None = Field(default=None, alias='d')

	class Config:		
		allow_mutation 			= True
		validate_assignment 	= True
		allow_population_by_field_name = True


class WGPlayerAchievements(JSONExportable):
	"""Placeholder class for data.achievements that are not collected"""
	class Config:		
		allow_mutation 			= True
		validate_assignment 	= True
		allow_population_by_field_name = True
		extra 					= Extra.allow


class WGPlayerAchievementsMaxSeries(JSONExportable):
	id 			: ObjectId | None	= Field(default=None, alias='_id')
	jointVictory: int 				= Field(default=0, alias='jv')
	account_id	: int		 		= Field(default=0, alias='a')	
	region		: Region 	| None 	= Field(default=None, alias='r')
	release 	: str 		| None	= Field(default=None, alias='u')
	added		: int 				= Field(default=epoch_now(), alias='t')

	_include_export_DB_fields	: ClassVar[Optional[TypeExcludeDict]] = { 	'id' 		: True, 
																			'jointVictory': True, 
																			'account_id': True, 
																			'region'	: True, 
																			'release'	: True,
																			'added'		: True
																		}

	_exclude_defaults = False
	class Config:		
		allow_mutation 			= True
		validate_assignment 	= True
		allow_population_by_field_name = True
		arbitrary_types_allowed = True
		json_encoders 			= { ObjectId: str }
		extra 					= Extra.allow
	

	@property
	def index(self) -> Idx:
		"""return backend index"""
		if self.id is None:
			return self.mk_index(self.account_id, self.region, self.added)
		else:
			return self.id


	@property
	def indexes(self) -> dict[str, Idx]:
		"""return backend indexes"""
		return { 'account_id': self.account_id, 'region': str(self.region), 'added': self.added }


	@classmethod
	def backend_indexes(cls) -> list[list[tuple[str, BackendIndexType]]]:
		indexes : list[list[BackendIndex]] = list()
		indexes.append([
					 	('region', ASCENDING), 
						('account_id', ASCENDING), 
						('added', DESCENDING)
						])
		indexes.append([
					 	('release', DESCENDING),	
						('region', ASCENDING),
						('account_id', ASCENDING), 
						('added', DESCENDING)
						])
		return indexes


	@classmethod
	def mk_index(cls, account_id : int, region: Region | None, added: int) -> ObjectId:
		r: int = 0
		if region is not None:
			r = list(Region).index(region)
		return ObjectId(hex(account_id)[2:].zfill(10) + hex(r)[2:].zfill(6) + hex(added)[2:].zfill(8))
	

	@root_validator
	def set_region_id(cls, values: dict[str, Any]) -> dict[str, Any]:
		r: int = 0
		region : Region | None 	= values['region']
		account_id : int 		= values['account_id']

		if region is None and account_id > 0:
			region = Region.from_id(account_id)
		values['region'] = region
		values['id'] = cls.mk_index(account_id, region, values['added'])
		# debug(f"account_id={account_id}, region={region}, added={values['added']}, _id = {values['id']}")
		return values


	def __str__(self) -> str:
		return f'account_id={self.account_id}:{self.region} added={self.added}'
	

	@classmethod
	def transform_WGPlayerAchievementsMain(cls, in_obj: 'WGPlayerAchievementsMain') -> Optional['WGPlayerAchievementsMaxSeries']:
		"""Transform WGPlayerAchievementsMain object to WGPlayerAchievementsMaxSeries"""
		try:
			if in_obj.max_series is None:
				raise ValueError(f"in_obj doesn't have 'max_series' set: {in_obj}")
			ms = in_obj.max_series
			if in_obj.account_id is None:
				raise ValueError(f"in_obj doesn't have 'account_id' set: {in_obj}")
			if in_obj.updated is None:
				ms.added = epoch_now()
			else:
				ms.added = in_obj.updated
			ms.account_id = in_obj.account_id
			return ms

		except Exception as err:
			error(f'{err}')
		return None


class WGPlayerAchievementsMain(JSONExportable):
	achievements 	: WGPlayerAchievements | None = Field(default=None, alias='a')
	max_series		: WGPlayerAchievementsMaxSeries | None = Field(default=None, alias='m')
	account_id 		: int | None 				= Field(default=None)
	updated			: int | None 				= Field(default=None)

	class Config:		
		allow_mutation 			= True
		validate_assignment 	= True
		allow_population_by_field_name = True


WGPlayerAchievementsMaxSeries.register_transformation(WGPlayerAchievementsMain, WGPlayerAchievementsMaxSeries.transform_WGPlayerAchievementsMain)


class WGApiWoTBlitzPlayerAchievements(WGApiWoTBlitz):	
	data	: dict[str, WGPlayerAchievementsMain] | None = Field(default=None, alias='d')

	class Config:		
		allow_mutation 			= True
		validate_assignment 	= True
		allow_population_by_field_name = True


	@validator('data', pre=True)
	def validate_data(cls, v : dict[str, WGPlayerAchievementsMain | None] | None) -> dict[str, WGPlayerAchievementsMain] | None:
		if not isinstance(v, dict):
			return None
		else:
			res : dict[str, WGPlayerAchievementsMain]
			res = { key:value for key, value in v.items() if value is not None }
			return res



	def get_max_series(self) -> list[WGPlayerAchievementsMaxSeries]:
		res : list[WGPlayerAchievementsMaxSeries] = list()
		try:			
			if self.data is None:
				return res
			for key, pam in self.data.items():
				try:
					if pam is None or pam.max_series is None:
						continue
					ms : WGPlayerAchievementsMaxSeries = pam.max_series
					account_id = int(key)
					ms.account_id = account_id
					if ms.region is None:
						if (region := Region.from_id(account_id)) is not None:
							ms.region = region
					res.append(ms)
				except Exception as err:
					error(f"Unknown error parsing 'max_series': {err}")
		except Exception as err:
			error(f"Error getting 'max_series': {err}")
		return res


	def set_regions(self, region: Region) -> None:
		try:			
			if self.data is None:
				return None
			for key, pam in self.data.items():
				try:
					if pam is None or pam.max_series is None:
						continue
					else:
						pam.max_series.region = region
						self.data[key].max_series = pam.max_series
				except Exception as err:
					error(f"Unknown error: {err}")
		except Exception as err:
			error(f"Error getting 'max_series': {err}")
		return None


class WGApiTankopedia(WGApiWoTBlitz):
	data 	: dict[str, Tank] | None = Field(default=None, alias='d')
	userStr	: dict[str, str] | None  = Field(default=None, alias='s')

	_exclude_export_DB_fields : ClassVar[Optional[TypeExcludeDict]] = {	'userStr': True }

	class Config:		
		allow_mutation 					= True
		validate_assignment 			= True
		allow_population_by_field_name 	= True


class WoTBlitzTankString(JSONExportable):
	code: str = Field(default=..., alias='_id')
	name: str = Field(default=..., alias='n')

	class Config:		
		allow_mutation 			= True
		validate_assignment 	= True
		allow_population_by_field_name = True


	@property
	def index(self) -> Idx:
		return self.code


	@property
	def indexes(self) -> dict[str, Idx]:
		"""return backend indexes"""
		return { 'code': self.index }


	@classmethod
	def backend_indexes(cls) -> list[list[tuple[str, BackendIndexType]]]:
		indexes : list[list[tuple[str, BackendIndexType]]] = list()
		indexes.append([ ('code', TEXT) ])
		return indexes


	@classmethod
	def from_tankopedia(cls, tankopedia: WGApiTankopedia) -> list['WoTBlitzTankString'] | None:
		res : list[WoTBlitzTankString] = list()
		try:
			if tankopedia.userStr is not None:
				for k, v in tankopedia.userStr.items():
					res.append(WoTBlitzTankString(code=k, name=v))
				return res
		except Exception as err:
			error(f"Could not read tank strings from Tankopedia: {err}")

		return None
