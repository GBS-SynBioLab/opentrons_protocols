def get_values(*names):
    import json
    _all_values = json.loads("""{"right_pipette_type":"p300_multi_gen2", "left_pipette_type":"p300_single","dilution_factor":1.5,"num_of_dilutions":10,"total_mixing_volume":200,"tip_use_strategy":"never", "initial_volume":200}""")
    return [_all_values[n] for n in names]


deck_config = {
    'tiprack': {'load_name': 'opentrons_96_tiprack_300ul', 'location': ['1']},
    'trough': {'load_name': 'nest_12_reservoir_15ml', 'location': '2'},
    'plate': {'load_name': 'corning_96_wellplate_360ul_flat', 'location': '3'},
    'tube_rack': {'load_name': 'opentrons_6_tuberack_falcon_50ml_conical', 'location': '5'}
}

metadata = {
    'protocolName': 'Customizable Serial Dilution',
    'author': 'Zoltan Tuza <ztuza@ic.ac.uk>',
    'source': 'GBS Protocol Library',
    'apiLevel': '2.7'
    }


def run(protocol_context):
    [right_pipette_type, left_pipette_type, dilution_factor, num_of_dilutions, total_mixing_volume,
        tip_use_strategy, initial_volume] = get_values(  # noqa: F821
            'right_pipette_type', 'right_pipette_type', 'dilution_factor', 'num_of_dilutions',
            'total_mixing_volume', 'tip_use_strategy', 'initial_volume'
        )

    # labware
    trough = protocol_context.load_labware(**deck_config['trough'])
    liquid_trash = trough.wells()[0]
    plate = protocol_context.load_labware(**deck_config['plate'])
    tiprack = [
        protocol_context.load_labware(deck_config['tiprack']['load_name'], slot)
        for slot in deck_config['tiprack']['location']
    ]

    sample_tubes = protocol_context.load_labware(**deck_config['tube_rack'])

    pipette = protocol_context.load_instrument(
        right_pipette_type, mount='right', tip_racks=tiprack)

    pipette_left = protocol_context.load_instrument(
        left_pipette_type, mount='left', tip_racks=tiprack)

    transfer_volume = total_mixing_volume/dilution_factor
    diluent_volume = total_mixing_volume - transfer_volume

    pipette_left.pick_up_tip(tiprack[0]['A12'])
    # part 1 transfer food dye to the wells
    pipette_left.transfer(volume=initial_volume,
                     source=sample_tubes.wells('A1'),
                     dest=plate.columns('1'),
                     liquid_trash=liquid_trash,
                     new_tip=tip_use_strategy
                     )
    pipette_left.drop_tip()

    # part 2 serial dilution
    if 'multi' in right_pipette_type:

        # Distribute diluent across the plate to the the number of samples
        # And add diluent to one column after the number of samples for a blank
        pipette.transfer(
            diluent_volume,
            trough.wells()[0],
            plate.rows()[0][1:1+num_of_dilutions]
        )

        # Dilution of samples across the 96-well flat bottom plate
        pipette.pick_up_tip()

        for s, d in zip(
                plate.rows()[0][:num_of_dilutions],
                plate.rows()[0][1:1+num_of_dilutions]
        ):
            pipette.transfer(
                transfer_volume,
                s,
                d,
                mix_after=(3, total_mixing_volume/2),
                new_tip=tip_use_strategy
            )

        # Remove transfer volume from the last column of the dilution
        pipette.transfer(
            transfer_volume,
            plate.rows()[0][num_of_dilutions],
            liquid_trash,
            new_tip=tip_use_strategy,
            blow_out=True
        )

        if tip_use_strategy == 'never':
            pipette.drop_tip()

    else:
        # Distribute diluent across the plate to the the number of samples
        # And add diluent to one column after the number of samples for a blank
        for col in plate.columns()[1:1+num_of_dilutions]:
            pipette.distribute(
                diluent_volume, trough.wells()[0], [well for well in col])

        for row in plate.rows():
            if tip_use_strategy == 'never':
                pipette.pick_up_tip()

            for s, d in zip(row[:num_of_dilutions], row[1:1+num_of_dilutions]):

                pipette.transfer(
                    transfer_volume,
                    s,
                    d,
                    mix_after=(3, total_mixing_volume/2),
                    new_tip=tip_use_strategy
                )

                pipette.transfer(
                    transfer_volume,
                    row[num_of_dilutions],
                    liquid_trash,
                    new_tip=tip_use_strategy,
                    blow_out=True
                )

            if tip_use_strategy == 'never':
                pipette.drop_tip()
