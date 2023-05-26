from datetime import datetime
from typing import Any, Tuple
from enum import IntEnum, StrEnum
from collections import defaultdict
import logging
from bson.objectid import ObjectId
from pydantic import BaseModel, Extra, root_validator, validator, Field, HttpUrl

from pyutils import JSONExportable, JSONImportable, Idx, BackendIndexType
from pyutils.exportable import	DESCENDING, ASCENDING, TEXT

from .tank import EnumVehicleTypeInt, EnumVehicleType

logger = logging.getLogger()
error 	= logger.error
message	= logger.warning
verbose	= logger.info
debug	= logger.debug


class EnumWinnerTeam(IntEnum):
	draw = 0
	one = 1
	two = 2


class EnumBattleResult(IntEnum):
	incomplete = -1
	not_win = 0
	win = 1
	loss = 2 	# not in replays
	draw = 3	# not in replays

	def __str__(self) -> str:
		return f'{self.name}'.capitalize()


class WoTBlitzMaps(StrEnum):
	Random			= "Random map"
	amigosville		= "Falls Creek"
	asia			= "Lost Temple"
	canal			= "Canal"
	canyon 			= "Canyon"
	desert_train 	= "Desert Sands"
	erlenberg 		= "Middleburg"
	faust 			= "Faust"
	fort 			= "Macragge"
	grossberg 		= "Dynasty's Pearl"
	himmelsdorf 	= "Himmelsdorf"
	italy 			= "Vineyards"
	karelia 		= "Rockfield"
	karieri 		= "Copperfield"
	lake 			= "Mirage"
	lumber			= "Alpenstadt"
	malinovka 		= "Winter Malinovka"
	medvedkovo 		= "Dead Rail"
	milbase 		= "Yamato Harbor"
	mountain 		= "Black Goldville"
	north 			= "North"
	ordeal 			= "Trial by Fire"
	pliego 			= "Castilla"
	port 			= "Port Bay"
	rock 			= "Mayan Ruins"
	rudniki 		= "Mines"
	savanna 		= "Oasis Palms"
	skit 			= "Naval Frontier"
	test 			= "World of Ducks"
	tutorial 		= "Proving Grounds"



###########################################
# 
# Replays
#
###########################################

class WoTBlitzReplayAchievement(BaseModel):
	t: int
	v: int


###########################################
# 
# WoTBlitzReplayDetail()
#
###########################################

class WoTBlitzReplayDetail(BaseModel):
	achievements : list[WoTBlitzReplayAchievement] | None = Field(default=None, alias='a')
	base_capture_points	: int | None = Field(default=None, alias='bc')
	base_defend_points	: int | None = Field(default=None, alias='bd')
	chassis_id			: int | None = Field(default=None, alias='ch')
	clan_tag			: str | None = Field(default=None, alias='ct')
	clanid				: int | None = Field(default=None, alias='ci')
	credits				: int | None = Field(default=None, alias='cr')
	damage_assisted		: int | None = Field(default=None, alias='da')
	damage_assisted_track: int | None = Field(default=None, alias='dat')
	damage_blocked		: int | None = Field(default=None, alias='db')
	damage_made			: int | None = Field(default=None, alias='dm')
	damage_received		: int | None = Field(default=None, alias='dr')
	dbid				: int  		 = Field(default=..., alias='ai')
	death_reason		: int | None = Field(default=None, alias='de')
	distance_travelled	: int | None = Field(default=None, alias='dt')
	enemies_damaged		: int | None = Field(default=None, alias='ed')
	enemies_destroyed	: int | None = Field(default=None, alias='ek')
	enemies_spotted		: int | None = Field(default=None, alias='es')
	exp					: int | None = Field(default=None, alias='ex')
	exp_for_assist		: int | None = Field(default=None, alias='exa')
	exp_for_damage		: int | None = Field(default=None, alias='exd')
	exp_team_bonus		: int | None = Field(default=None, alias='et')
	gun_id				: int | None = Field(default=None, alias='gi')
	hero_bonus_credits	: int | None = Field(default=None, alias='hc')
	hero_bonus_exp		: int | None = Field(default=None, alias='he')
	hitpoints_left		: int | None = Field(default=None, alias='hl')
	hits_bounced		: int | None = Field(default=None, alias='hb')
	hits_pen			: int | None = Field(default=None, alias='hp')
	hits_received		: int | None = Field(default=None, alias='hr')
	hits_splash			: int | None = Field(default=None, alias='hs')
	killed_by			: int | None = Field(default=None, alias='ki')
	shots_hit			: int | None = Field(default=None, alias='sh')
	shots_made			: int | None = Field(default=None, alias='sm')
	shots_pen			: int | None = Field(default=None, alias='sp')
	shots_splash		: int | None = Field(default=None, alias='ss')
	squad_index			: int | None = Field(default=None, alias='sq')
	time_alive			: int | None = Field(default=None, alias='t')
	turret_id			: int | None = Field(default=None, alias='ti')
	vehicle_descr		: int | None = Field(default=None, alias='vi')
	wp_points_earned	: int | None = Field(default=None, alias='we')
	wp_points_stolen	: int | None = Field(default=None, alias='ws')

	class Config:
		extra 				= Extra.allow
		allow_mutation 		= True
		validate_assignment = True
		allow_population_by_field_name = True


###########################################
# 
# WoTBlitzReplaySummary()
#
###########################################

class WoTBlitzReplaySummary(BaseModel):
	_TimestampFormat : str = "%Y-%m-%d %H:%M:%S"

	winner_team 	: EnumWinnerTeam 	| None 	= Field(default=..., alias='wt')
	battle_result 	: EnumBattleResult 	| None 	= Field(default=..., alias='br')
	room_type		: int | None 	= Field(default=None, alias='rt')
	battle_type		: int | None 	= Field(default=None, alias='bt')
	uploaded_by 	: int 			= Field(default=0, alias='ul')
	title 			: str | None 	= Field(default=..., alias='t')
	player_name		: str			= Field(default=..., alias='pn')
	protagonist		: int 			= Field(default=..., alias='p')
	protagonist_team: int | None	= Field(default=..., alias='pt')
	map_name		: str			= Field(default=..., alias='mn')
	vehicle			: str			= Field(default=..., alias='v')
	vehicle_tier	: int | None	= Field(default=..., alias='vx')
	vehicle_type 	: EnumVehicleType | None = Field(default=..., alias='vt')
	credits_total	: int | None 	= Field(default=None, alias='ct')
	credits_base	: int | None 	= Field(default=None, alias='cb')
	exp_base		: int | None	= Field(default=None, alias='eb')
	exp_total		: int | None	= Field(default=None, alias='et')
	battle_start_timestamp : int	= Field(default=..., alias='bts')
	battle_start_time : str | None	= Field(default=None, repr=False)	# duplicate of 'bts'
	battle_duration : float			= Field(default=..., alias='bd')
	description		: str |None		= Field(default=None, alias='de')
	arena_unique_id	: int			= Field(default=..., alias='aid')
	allies 			: list[int]		= Field(default=..., alias='a')
	enemies 		: list[int]		= Field(default=..., alias='e')
	mastery_badge	: int | None 	= Field(default=None, alias='mb')
	details 		: list[WoTBlitzReplayDetail] = Field(default=..., alias='d')


	class Config:
		extra 				= Extra.allow
		allow_mutation 		= True
		validate_assignment = True
		allow_population_by_field_name = True


	@validator('vehicle_tier')
	def check_tier(cls, v : int | None) -> int | None:
		if v is not None:
			if v > 10 or v < 0:
				raise ValueError('Tier has to be within [1, 10]')
		return v


	@validator('protagonist_team')
	def check_protagonist_team(cls, v : int) -> int | None:
		if v is None: 
			return None
		elif v == 0 or v == 1 or v == 2:
			return v
		else:
			raise ValueError('protagonist_team has to be 0, 1, 2 or None')


	@validator('battle_start_time')
	def return_none(cls, v : str) -> None:
		return None


	@root_validator(skip_on_failure=True)
	def root(cls, values : dict[str, Any]) ->  dict[str, Any]:
		values['battle_start_time'] = datetime.fromtimestamp(values['battle_start_timestamp']).strftime(cls._TimestampFormat)
		return values



###########################################
# 
# WoTBlitzReplayData()
#
###########################################

class WoTBlitzReplayData(JSONExportable, JSONImportable):
	id 			: str | None		= Field(default=None, alias='_id')
	view_url	: HttpUrl | None	= Field(default=None, alias='v')
	download_url: HttpUrl | None	= Field(default=None, alias='d')
	summary		: WoTBlitzReplaySummary  = Field(default=..., alias='s')

	_ViewUrlBase : str = 'https://replays.wotinspector.com/en/view/'
	_DLurlBase	: str = 'https://replays.wotinspector.com/en/download/'

	class Config:
		arbitrary_types_allowed = True
		allow_mutation 			= True
		validate_assignment 	= True
		allow_population_by_field_name = True
		json_encoders = { ObjectId: str }

	_exclude_export_DB_fields	= { 'view_url': True,
									'download_url': True,
									'summary': { 'battle_start_time' }
									}


	@property
	def index(self) -> Idx:
		"""return backend index"""
		if self.id is not None:
			return self.id
		raise ValueError('id is missing')


	@property
	def indexes(self) -> dict[str, Idx]:
		"""return backend indexes"""
		return { 'id': self.index }


	@classmethod
	def backend_indexes(cls) -> list[list[tuple[str, BackendIndexType]]]:
		"""return backend search indexes"""
		indexes : list[list[tuple[str, BackendIndexType]]] = list()
		indexes.append([('summary.protagonist', ASCENDING), 
						('summary.room_type', ASCENDING), 
						('summary.vehicle_tier', ASCENDING), 
						('summary.battle_start_timestamp', DESCENDING)
					])
		indexes.append([('summary.room_type', ASCENDING), 
						('summary.vehicle_tier', ASCENDING),
						('summary.battle_start_timestamp', DESCENDING)
					])
		return indexes


	@classmethod
	def transform_WoTBlitzReplayJSON(cls, in_obj: 'WoTBlitzReplayJSON') -> 'WoTBlitzReplayData':
		return in_obj.data
		
	
	@root_validator
	def store_id(cls, values : dict[str, Any]) -> dict[str, Any]:
		try:
			debug('validating: WoTBlitzReplayData()')
			id : str
			if values['id'] is not None:
				debug('data.id found')
				id = values['id']
			elif values['view_url'] is not None:
				id = values['view_url'].split('/')[-1:][0]
			elif values['download_url'] is not None:
				id = values['download_url'].split('/')[-1:][0]
			else:
				debug('could not modify id')
				return values  # could not modify 'id'
				# raise ValueError('Replay ID is missing')
			values['id']			= id
			values['view_url'] 		= f"{cls._ViewUrlBase}{id}"
			values['download_url'] 	= f"{cls._DLurlBase}{id}"
			return values
		except Exception as err:
			raise ValueError(f'Error reading replay ID: {err}')



###########################################
# 
# WoTBlitzReplayJSON()
#
###########################################

		
class WoTBlitzReplayJSON(JSONExportable, JSONImportable):
	id 		: str | None 		= Field(default=None, alias='_id')
	status	: str				= Field(default="ok", alias='s')
	data	: WoTBlitzReplayData= Field(default=..., alias='d')
	error	: dict				= Field(default={}, alias='e')
	_URL_REPLAY_JSON : str 		= 'https://api.wotinspector.com/replay/upload?details=full&key='

	_exclude_export_src_fields 	= { 'id': True, 'data': { 'id': True }}
	_exclude_export_DB_fields	= { 'data': {
											'id': True,
											'view_url': True,
											'download_url': True,
											'summary': { 'battle_start_time' }
											}
									}

	class Config:
		arbitrary_types_allowed = True
		json_encoders 			= { ObjectId: str }
		allow_mutation 			= True
		validate_assignment 	= True
		allow_population_by_field_name = True


	@property
	def index(self) -> Idx:
		"""return backend index"""
		if self.id is not None:
			return self.id
		raise ValueError('id is missing') 


	@property
	def indexes(self) -> dict[str, Idx]:
		"""return backend indexes"""
		return { 'id': self.index }


	@root_validator(pre=False)
	def store_id(cls, values : dict[str, Any]) -> dict[str, Any]:
		try:
			debug('validating: WoTBlitzReplayJSON(pre=False)')
			if 'id' not in values or values['id'] is None:
				values['id'] = values['data'].id
				debug(f"adding ROOT.id")
			elif 'id' in values and values['id'] is not None:
				debug(f"adding data.id from ROOT.id")
				values['data'].id = values['id']		
			return values
		except Exception as err:
			raise ValueError(f'Could not store replay ID: {err}')


	def get_id(self) -> str | None:
		try:
			if self.id is not None:
				return self.id
			else:
				return self.data.id
		except Exception as err:
			error(f'Could not read replay id: {err}')
		return None


	def get_url_json(self) -> str:
		return f'{self._URL_REPLAY_JSON}{self.id}'


	def get_enemies(self, player: int | None = None) -> list[int]:
		if player is None or (player in self.data.summary.allies):
			return self.data.summary.enemies
		elif player in self.data.summary.enemies:
			return self.data.summary.allies
		else:
			raise ValueError(f"account_id {player} not found in replay")


	def get_allies(self, player: int | None = None) -> list[int]:
		if player is None or (player in self.data.summary.allies):
			return self.data.summary.allies
		elif player in self.data.summary.enemies:
			return self.data.summary.enemies
		else:
			raise ValueError(f"player {player} not found in replay")


	def get_players(self) -> list[int]:
		return self.get_enemies() + self.get_allies()


	def get_platoons(self, player: int | None = None) -> Tuple[	defaultdict[int, list[int]],
																defaultdict[int, list[int]]]:
		allied_platoons : defaultdict[int, list[int]] = defaultdict(list)
		enemy_platoons 	: defaultdict[int, list[int]] = defaultdict(list)

		allies 	= self.get_allies(player)

		for d in self.data.summary.details:
			if d.squad_index is not None and d.squad_index > 0:
				account_id = d.dbid
				if account_id in allies:
					allied_platoons[d.squad_index].append(account_id)
				else:
					enemy_platoons[d.squad_index].append(account_id)

		return allied_platoons, enemy_platoons


	def get_battle_result(self, player : int | None = None) -> EnumBattleResult:
		try:
			if self.data.summary.battle_result == EnumBattleResult.incomplete:
				return EnumBattleResult.incomplete

			elif player is not None and player in self.get_enemies():
				if self.data.summary.battle_result == EnumBattleResult.win:
					return EnumBattleResult.loss
				elif self.data.summary.winner_team == EnumWinnerTeam.draw:
					return EnumBattleResult.draw
				else:
					return EnumBattleResult.win

			elif player is None or player in self.get_allies():
				if self.data.summary.battle_result == EnumBattleResult.win:
					return EnumBattleResult.win
				elif self.data.summary.winner_team == EnumWinnerTeam.draw:
					return EnumBattleResult.draw
				else:
					return EnumBattleResult.loss
			else:
				debug(f"player ({str(player)}) not in the battle")
				return EnumBattleResult.incomplete
		except Exception as err:
			raise Exception('Error reading replay')


WoTBlitzReplayData.register_transformation(WoTBlitzReplayJSON,WoTBlitzReplayData.transform_WoTBlitzReplayJSON )
