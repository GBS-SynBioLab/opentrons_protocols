import opentrons.simulate


def main():
    file_name = 'test_thermocycler'
    protocol_path = '../tests/%s.py' % file_name

    with open(protocol_path) as protocol_file:
        runlog = opentrons.simulate.simulate(protocol_file=protocol_file, file_name=file_name)
        print(opentrons.simulate.format_runlog(runlog[0]))

    print('program done')


if __name__ == '__main__':
    main()
