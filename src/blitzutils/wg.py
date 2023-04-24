import logging
from typing import Dict, Tuple,  Sequence
from collections import defaultdict
from aiohttp import ClientTimeout
from urllib.parse import quote

from pyutils.throttledclientsession import ThrottledClientSession
from pyutils.utils import get_url_JSON_model

from .models import Region, WGApiWoTBlitzTankStats, WGTankStat,\
					WGApiWoTBlitzPlayerAchievements, \
					WGPlayerAchievementsMaxSeries, \
					WGAccountInfo, WGApiWoTBlitzAccountInfo


TYPE_CHECKING = True
logger = logging.getLogger()
error 	= logger.error
message	= logger.warning
verbose	= logger.info
debug	= logger.debug

class WGApi():

	# constants
	DEFAULT_WG_APP_ID 		: str = '81381d3f45fa4aa75b78a7198eb216ad'
	DEFAULT_LESTA_APP_ID 	: str = ''

	URL_SERVER = {
		'eu'    : 'https://api.wotblitz.eu/wotb/',
		'ru'    : 'https://api.wotblitz.ru/wotb/',
		'com'   : 'https://api.wotblitz.com/wotb/',
		'asia'  : 'https://api.wotblitz.asia/wotb/',
		'china' : None
		}

	def __init__(self, 
				app_id 		: str = DEFAULT_WG_APP_ID, 
				ru_app_id	: str = DEFAULT_LESTA_APP_ID,
				# tankopedia_fn 	: str = 'tanks.json', 
				# maps_fn 		: str = 'maps.json', 
				rate_limit: float = 10, 
				ru_rate_limit: float = -1):
		assert app_id is not None, "WG App ID must not be None"
		assert rate_limit is not None, "rate_limit must not be None"
		debug(f'rate_limit: {rate_limit}')
		self.app_id  	: str = app_id
		self.ru_app_id 	: str = ru_app_id
		self.session 	: dict[str, ThrottledClientSession] = dict()

		if ru_rate_limit < 0:
			ru_rate_limit = rate_limit

		headers = {'Accept-Encoding': 'gzip, deflate'} 	
		
		for region in [ Region.eu, Region.com, Region.asia ]:
			timeout = ClientTimeout(total=10)
			self.session[region.value] = ThrottledClientSession(rate_limit=rate_limit, 
																headers=headers, 
																timeout=timeout)
		for region in [ Region.ru ]:
			timeout = ClientTimeout(total=10)
			self.session[region.value] = ThrottledClientSession(rate_limit=ru_rate_limit, 
																headers=headers, 
																timeout=timeout)
		debug('WG aiohttp session initiated')            
		

	async def close(self) -> None:
		"""Close aiohttp sessions"""
		for server in self.session.keys():
			try:
				debug(f'trying to close session to {server} server')
				await self.session[server].close()
				debug(f'session to {server} server closed')
			except Exception as err:
				error(f'{err}')
		return None
	
	
	def stats(self) -> dict[str, str] | None:
		"""Return dict of stats per server"""		
		try:
			totals : defaultdict[str, float] = defaultdict(float)
			stats_dict : dict[str, dict[str, float]] = dict()
			for region in self.session.keys():

				if self.session[region].stats_dict['count'] > 0:
					stats_dict[region] = self.session[region].stats_dict
			
			res : dict[str, str] = dict()
			for region in stats_dict:
				res[region] = ThrottledClientSession.print_stats(stats_dict[region])
					
			if len(stats_dict) > 1:
				for region in stats_dict:
					for stat in stats_dict[region]:
						totals[stat] += stats_dict[region][stat]
				res['Total'] = ThrottledClientSession.print_stats(totals)	
			return res
		except Exception as err:
			error(f'{err}')
		return None


	def print(self) -> None:
		"""Print server stats"""
		try:
			stats : dict[str, str] | None = self.stats()
			if stats is not None:
				message('WG API stats:')
				for server in stats:
					message(f'{server.capitalize():7s}: {stats[server]}') 
		except Exception as err:
			error(f'{err}')


	@classmethod
	def get_server_url(cls, region: Region) -> str | None:
		assert region is not None, "region must not be None"		
		try:
			return cls.URL_SERVER[region.value]
		except Exception as err:
			error(f'Unknown region: {region.value}')
		return None

	###########################################
	# 
	# get_tank_stats()
	#
	###########################################	

	def get_tank_stats_url(self, account_id : int , region: Region, 
							tank_ids: list[int] = [], fields: list[str] = []) -> Tuple[str, Region] | None:
		assert type(account_id) is int, "account_id must be int"
		assert type(tank_ids) is list,	"tank_ids must be a list"
		assert type(fields) is list,	"fields must be a list"
		assert type(region) is Region,	"region must be type of Region"
		try:
			URL_WG_TANK_STATS: str = 'tanks/stats/'

			account_region : Region | None = Region.from_id(account_id)
			
			if account_region is None:
				raise ValueError('Could not determine region for account_id')
			if account_region != region:
				raise ValueError(f'account_id {account_id} does not match region {region.name}')
						
			server : str | None = self.get_server_url(account_region)
			if server is None:
				raise ValueError(f'No API server for region {account_region.value}')
			
			tank_id_str : str = ''
			if len(tank_ids) > 0:
				tank_id_str = '&tank_id=' + quote(','.join([ str(x) for x in tank_ids]))
			
			field_str : str = ''
			if len(fields) > 0:
				field_str = '&fields=' + quote(','.join(fields))
			if region == Region.ru:
				return f'{server}{URL_WG_TANK_STATS}?application_id={self.ru_app_id}&account_id={account_id}{tank_id_str}{field_str}', account_region
			else:
				return f'{server}{URL_WG_TANK_STATS}?application_id={self.app_id}&account_id={account_id}{tank_id_str}{field_str}', account_region
		except Exception as err:
			debug(f'Failed to form url for account_id: {account_id}: {err}')
		return None

	
	async def get_tank_stats_full(self, account_id: int, region: Region,
				tank_ids: list[int] = [], fields: list[str] = [] ) -> WGApiWoTBlitzTankStats | None:
		try:
			server_url : Tuple[str, Region] | None = self.get_tank_stats_url(account_id=account_id, region=region, tank_ids=tank_ids, fields=fields)
			if server_url is None:
				raise ValueError(f'No tank stats available')
			url : str = server_url[0]
			region = server_url[1]

			return await get_url_JSON_model(self.session[region.value], url, resp_model=WGApiWoTBlitzTankStats)
			
		except Exception as err:
			error(f'Failed to fetch tank stats for account_id: {account_id}: {err}')
		return None	

	
	async def get_tank_stats(self, account_id: int, region: Region,
			tank_ids: list[int] = [], fields: list[str] = [] ) -> list[WGTankStat] | None:
		try:
			resp : WGApiWoTBlitzTankStats | None = await self.get_tank_stats_full(account_id=account_id, region=region, tank_ids=tank_ids, fields=fields)
			if resp is None or resp.data is None:
				verbose(f'could not fetch tank stats for account_id={account_id}:{region}')
				return None
			else:
				return list(resp.data.values())[0]
		except Exception as err:
			debug(f'Failed to fetch tank stats for account_id: {account_id}: {err}')
		return None	
		

	###########################################
	# 
	# get_account_info()
	#
	###########################################

	def get_account_info_url(self, 
							  account_ids : Sequence[int], 
							  region: Region, 
							  fields: list[str] = ['account_id', 
													'created_at', 
													'updated_at', 
													'last_battle_time', 
													'nickname']) -> str | None:
		"""get URL for /wotb/account/info/"""
		URL_WG_ACCOUNT_INFO: str = 'account/info/'
		try:
			debug(f'starting, account_ids={account_ids}, region={region}')
			server : str | None
			if (server :=  self.get_server_url(region)) is None:
				raise ValueError(f'No API server for region {region}')
			if len(account_ids) == 0:
				raise ValueError('Empty account_id list given')
			
			account_str: str = quote(','.join([ str(a) for a in account_ids] ))			
			field_str : str = ''
			if len(fields) > 0:
				field_str = '&fields=' + quote(','.join(fields))
			if region == Region.ru:
				return f'{server}{URL_WG_ACCOUNT_INFO}?application_id={self.ru_app_id}&account_id={account_str}{field_str}'
			else:
				return f'{server}{URL_WG_ACCOUNT_INFO}?application_id={self.app_id}&account_id={account_str}{field_str}'
		except Exception as err:
			debug(f'Failed to form url: {err}')
		return None


	async def get_account_info_full(self, 
									account_ids : Sequence[int], 
									region: Region,
									fields: list[str] = ['account_id', 
														'created_at', 
														'updated_at', 
														'last_battle_time', 
														'nickname'] 
										) -> WGApiWoTBlitzAccountInfo | None:
		"""get WG API response for account/info"""		
		try:
			url : str | None
			if (url := self.get_account_info_url(account_ids=account_ids, region=region, fields=fields)) is None:
				raise ValueError(f'No account info available')
			debug(f'URL: {url}')
			return await get_url_JSON_model(self.session[region.value], url, resp_model=WGApiWoTBlitzAccountInfo)
			
		except Exception as err:
			error(f'Failed to fetch account info: {err}')
		return None	

	
	async def get_account_info(self, 
								account_ids : Sequence[int], 
								region: Region,
								fields: list[str] = ['account_id', 
													'created_at', 
													'updated_at', 
													'last_battle_time', 
													'nickname'] 
								) -> list[WGAccountInfo] | None:
		try:
			resp : WGApiWoTBlitzAccountInfo | None 
			resp = await self.get_account_info_full(account_ids=account_ids, region=region, fields=fields)
			if resp is None or resp.data is None:
				error('No stats found')
				return None
			else:				
				return [ info for info in resp.data.values() if info is not None ]
		except Exception as err:
			error(f'Failed to fetch player achievements: {err}')
		return None	


	###########################################
	# 
	# get_player_achievements()
	#
	###########################################

	def get_player_achievements_url(self, account_ids : Sequence[int], 
									region: Region, 
									fields: list[str] = list()) -> str | None:
		URL_WG_PLAYER_ACHIEVEMENTS: str = 'account/achievements/'
		try:
			debug(f'starting, account_ids={account_ids}, region={region}')
			server : str | None = self.get_server_url(region)
			if server is None:
				raise ValueError(f'No API server for region {region}')
			if len(account_ids) == 0:
				raise ValueError('Empty account_id list given')
			
			account_str: str = quote(','.join([ str(a) for a in account_ids] ))			
			field_str : str = ''
			if len(fields) > 0:
				field_str = '&fields=' + quote(','.join(fields))
			if region == Region.ru:
				return f'{server}{URL_WG_PLAYER_ACHIEVEMENTS}?application_id={self.ru_app_id}&account_id={account_str}{field_str}'
			else:
				return f'{server}{URL_WG_PLAYER_ACHIEVEMENTS}?application_id={self.app_id}&account_id={account_str}{field_str}'
		except Exception as err:
			debug(f'Failed to form url: {err}')
		return None

	
	async def get_player_achievements_full(self, account_ids : list[int], region: Region,
											fields: list[str] = list() ) -> WGApiWoTBlitzPlayerAchievements | None:
		try:
			url : str | None
			if (url := self.get_player_achievements_url(account_ids=account_ids, region=region, fields=fields)) is None:
				raise ValueError(f'No player achievements available')
			debug(f'URL: {url}')
			return await get_url_JSON_model(self.session[region.value], url, resp_model=WGApiWoTBlitzPlayerAchievements)
			
		except Exception as err:
			error(f'Failed to fetch player achievements: {err}')
		return None	

	
	async def get_player_achievements(self, account_ids : list[int], 
										region: Region,
										fields: list[str] = list() ) -> list[WGPlayerAchievementsMaxSeries] | None:
		try:
			resp : WGApiWoTBlitzPlayerAchievements | None 
			resp = await self.get_player_achievements_full(account_ids=account_ids, region=region, fields=fields)
			if resp is None or resp.data is None:
				error('No stats found')
				return None
			else:
				resp.set_regions(region)
				return resp.get_max_series()
		except Exception as err:
			error(f'Failed to fetch player achievements: {err}')
		return None	

# class Tankopedia():
# 	_tanks : Dict[int, Dict[str, int | str | bool]] | None = None


class WoTBlitzMaps():
	_maps : Dict[str, str] = {
		"Random": "Random map",
		"amigosville": "Falls Creek",
		"asia": "Lost Temple",
		"canal": "Canal",
		"canyon": "Canyon",
		"desert_train": "Desert Sands",
		"erlenberg": "Middleburg",
		"faust": "Faust",
		"fort": "Macragge",
		"grossberg": "Dynasty's Pearl",
		"himmelsdorf": "Himmelsdorf",
		"italy": "Vineyards",
		"karelia": "Rockfield",
		"karieri": "Copperfield",
		"lake": "Mirage",
		"lumber": "Alpenstadt",
		"malinovka": "Winter Malinovka",
		"medvedkovo": "Dead Rail",
		"milbase": "Yamato Harbor",
		"mountain": "Black Goldville",
		"north": "North",
		"ordeal": "Trial by Fire",
		"pliego": "Castilla",
		"port": "Port Bay",
		"rock": "Mayan Ruins",
		"rudniki": "Mines",
		"savanna": "Oasis Palms",
		"skit": "Naval Frontier",
		"test": "World of Ducks",
		"tutorial": "Proving Grounds"
	}
		