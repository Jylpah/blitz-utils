import sys
import pytest # type: ignore
from os.path import dirname, realpath, join as pjoin
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.resolve() / 'src'))

from blitzutils import Tank, WGTank, EnumNation, EnumVehicleTier, \
						EnumVehicleTypeInt, EnumVehicleTypeStr, EnumVehicleType


########################################################
#
# Test Plan
#
########################################################

# EnumVehicleTypeInt/Str
# 1) Test creation
# 2) Test conversions
# 3) Test equality (pass/fail)
# 3) Test errors

@pytest.fixture
def enum_vehicle_type_names() -> list[str]:
	return [ 'light_tank', 'medium_tank', 'heavy_tank', 'tank_destroyer' ]

@pytest.fixture
def enum_vehicle_type_api_names() -> list[str]:
	return [ 'lightTank', 'mediumTank', 'heavyTank', 'AT-SPG' ]

@pytest.fixture
def enum_vehicle_tier() -> list[str]:
	return [ 'I', 'II', 'III', 'IV', 'V', 'VI', 'VII', 'VIII', 'IX', 'X' ]

@pytest.fixture
def enum_nation() -> list[str]:
	return [ 'ussr', 'germany', 'usa', 'china', 'france', 'uk', 'japan', 'other', 'european' ]


def test_1_EnumVehicleTypeInt_create(enum_vehicle_type_names : list[str]) -> None:
	for ndx in range(len(enum_vehicle_type_names)):
		tank_type : str = enum_vehicle_type_names[ndx]
		try:
			assert EnumVehicleTypeInt(ndx) is EnumVehicleTypeInt[tank_type], \
					f"Creation of EnumVehicleTypeInt.{tank_type} failed"
		except Exception as err:
			assert False, f"Could not create EnumVehicleTypeInt of {tank_type}"


def test_2_EnumVehicleTypeInt_complete(enum_vehicle_type_names: list[str]) -> None:
	tank_types = set(EnumVehicleTypeInt)
	assert len(tank_types) == len(enum_vehicle_type_names), \
			f"EnumVehicleTypeInt has wrong number of tank types"
	for tank_type in enum_vehicle_type_names:
		tank_types.remove(EnumVehicleTypeInt[tank_type])
	assert len(tank_types) == 0, \
		f"EnumVehicleTypeInt does not have all the tank types: {' ,'.join([tti.name for tti in tank_types])}"


def test_3_EnumVehicleTypeStr_create(enum_vehicle_type_names : list[str] , 
									 enum_vehicle_type_api_names : list[str]
									 ) -> None:
	for ndx in range(len(enum_vehicle_type_names)):
		name 	: str = enum_vehicle_type_names[ndx]
		value 	: str = enum_vehicle_type_api_names[ndx]
		try:
			assert EnumVehicleTypeStr(value) is EnumVehicleTypeStr[name], \
					f"Creation of EnumVehicleTypeStr.{name} failed"
		except Exception as err:
			assert False, f"Could not create EnumVehicleTypeStr.{name}"


def test_4_EnumVehicleTypestr_complete(enum_vehicle_type_names: list[str]) -> None:
	tank_types = set(EnumVehicleTypeStr)
	assert len(tank_types) == len(enum_vehicle_type_names), \
			f"EnumVehicleTypeStr has wrong number of tank types"
	for tank_type in enum_vehicle_type_names:
		tank_types.remove(EnumVehicleTypeStr[tank_type])
	assert len(tank_types) == 0, \
		f"EnumVehicleTypeStr does not have all the tank types: {' ,'.join([tts.name for tts in tank_types])}"  # type: ignore
	

# def test_5_EnumVehicleType_conversion() -> None:
# 	"""Test converstions between EnumVehicleTypeInt and EnumVehicleTypeStr"""
# 	for tt_int in EnumVehicleTypeInt:
# 		tt_str = EnumVehicleTypeStr(tt_int)
# 		assert tt_int.name == tt_str.name, \
# 				f'Conversion from EnumVehicleTypeInt to EnumVehicleTypeStr failed: {tt_int.name}'
# 		assert EnumVehicleTypeInt[tt_str.value] is tt_int, f"from_str() failed for {tt_str}"
# 		assert tt_int is tt_str.int_type, \
# 				f'Conversion from EnumVehicleTypeStr to EnumVehicleTypeInt failed: {tt_int.name}'
# 		assert EnumVehicleTypeStr[tt_int.value] is tt_str, f"from_int() failed for {tt_int}"
		

def test_6_EnumVehicleTier_create(enum_vehicle_tier) -> None:
	for ndx in range(len(enum_vehicle_tier)):
		tier_str : str = enum_vehicle_tier[ndx]
		tier_int : int = ndx + 1

		assert EnumVehicleTier(tier_int) is EnumVehicleTier[tier_str], f"Failed to create EnumVehicleTier for {tier_str}"
		assert EnumVehicleTier.read_tier(tier_str) is EnumVehicleTier[tier_str], f"read_tier({tier_str}) failed"
		assert EnumVehicleTier.read_tier(str(tier_int)) is EnumVehicleTier[tier_str], f"read_tier({tier_int}) failed"


def	test_7_EnumVehicleType_create(enum_vehicle_type_names : list[str] , 
								  enum_vehicle_type_api_names : list[str]
								  ) -> None:
	for ndx in range(len(enum_vehicle_type_names)):
		tank_type : str = enum_vehicle_type_names[ndx]
		api_name: str= enum_vehicle_type_api_names[ndx]
		try:
			assert EnumVehicleType(ndx) is EnumVehicleType(tank_type), \
					f"Creation of EnumVehicleType.{tank_type} failed"
			assert EnumVehicleType(tank_type) is EnumVehicleType(api_name), \
					f"Creation of EnumVehicleType.{tank_type} failed"
		except Exception as err:
			assert False, f"Could not create EnumVehicleTypeInt of {tank_type}"


def test_8_EnumVehicleType_complete(enum_vehicle_type_names: list[str]) -> None:
	tank_types = set(EnumVehicleType)
	assert len(tank_types) == len(enum_vehicle_type_names), \
			f"EnumVehicleTypeInt has wrong number of tank types"
	for tank_type in enum_vehicle_type_names:
		tank_types.remove(EnumVehicleType[tank_type])
	assert len(tank_types) == 0, \
		f"EnumVehicleTypeInt does not have all the tank types: {' ,'.join([tti.name for tti in tank_types])}"
