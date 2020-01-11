# Generic/Built-in
import collections
# Other Libs
from opentrons import protocol_api

__author__ = "Zoltan Tuza"
__copyright__ = "Copyright 2019, Imperial GBS Opentrons project"
__credits__ = ["Zoltan Tuza"]
__license__ = "GPL 3.0"
__version__ = "0.1.0"
__maintainer__ = "Zoltan Tuza"
__email__ = "zoltuz@gmail.com"
__status__ = "Dev"

metadata = {'apiLevel': '2.1'}

# a named tuple is used to keep the tempeture profile and its repetition together
stage_description = collections.namedtuple('thermocycler_stage', 'stage_profile repetition')

# ordered dict is used to keep the stages in the same order
stages = collections.OrderedDict()

stage_1_temp_profile = [
    {'temperature': 98, 'hold_time_seconds': 30},
]
stages['stage1'] = stage_description(stage_profile=stage_1_temp_profile, repetition=1)

stage_2_temp_profile = [
    {'temperature': 98, 'hold_time_seconds': 5},
    {'temperature': 67, 'hold_time_seconds': 10},
    {'temperature': 72, 'hold_time_seconds': 10},
]
stages['stage2'] = stage_description(stage_profile=stage_2_temp_profile, repetition=15)

stage_3_temp_profile = [
    {'temperature': 72, 'hold_time_seconds': 60},
]
stages['stage3'] = stage_description(stage_profile=stage_3_temp_profile, repetition=1)

# pcr settings (all temperature is in celsius and all volume is in microliter)
lid_temperature = 105
pcr_max_volume = 50
hold_temp = 4

# deck layout
source_plate_position = 1
tiprack_position = 2


def run(protocol: protocol_api.ProtocolContext):

    # labware
    tc_mod = protocol.load_module('Thermocycler Module')
    source_plate = protocol.load_labware('corning_96_wellplate_360ul_flat', source_plate_position)
    dest_plate = tc_mod.load_labware('nest_96_wellplate_100ul_pcr_full_skirt')
    tiprack_1 = protocol.load_labware('opentrons_96_tiprack_300ul', tiprack_position)
    p300 = protocol.load_instrument('p300_single', 'right', tip_racks=[tiprack_1])

    tc_mod.close_lid()

    tc_mod.set_lid_temperature(lid_temperature)

    # cycling through the stages
    for stage in stages.values():
        tc_mod.execute_profile(steps=stage.stage_profile, repetitions=stage.repetition, block_max_volume=pcr_max_volume)

    # hold stage
    tc_mod.set_block_temperature(hold_temp)
