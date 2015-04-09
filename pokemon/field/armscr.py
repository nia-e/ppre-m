
"""Generate script command arguments from the ARM binaries

Example usage:
`python -m pokemon.field.armscr projects/diamond/`
"""

import json
import struct

from pokemon.game import Game
from pokemon.field.script import Script
from util.io import BinaryIO
from arm.thumb import Thumb


command_info = {
    'Diamond': {
        'table_ofs': 0xf355c,
        'count': 720,
        'functions': {
            0x38c30: 'read16',
            0x38c48: 'read32'
        }
    },
    'Platinum': {
        'table_ofs': 0xeac58,
        'count': 720,  # ?
    },
    'HeartGold': {
        'table_ofs': 0xfad00,
        'count': 853,
        'functions': {
            0x3fe2c: 'read16',
            0x3fe44: 'read32'
        }
    }
}


if __name__ == '__main__':
    import os
    import sys

    target_game = Game.from_workspace(sys.argv[1])

    try:
        os.remove(os.path.join(target_game.files.directory, 'commands.json'))
    except OSError:
        pass
    script = Script(target_game)
    old_commands = script.commands

    with open(os.path.join(target_game.files.directory, 'header.bin'))\
            as header:
        header.seek(0x24)
        entry, ram_offset, size = struct.unpack('III', header.read(12))

    with open(os.path.join(target_game.files.directory, 'arm9.dec.bin'))\
            as handle:
        cmd_info = command_info[target_game.game_name]
        handle.seek(cmd_info['table_ofs'])
        offsets = struct.unpack('I'*cmd_info['count'],
                                handle.read(cmd_info['count']*4))

        decompiler = Thumb(handle)
        decompiler.functions = cmd_info['functions']

        skip = 0
        commands = {}
        for i, offset in enumerate(offsets):
            print(i, hex(offset))
            decompiler.start = (offset & 0xFFFFFFFE) - ram_offset - 4
            decompiler.reset()
            if decompiler.read_value(4) is None:
                skip += 1
                continue
            decompiler.parse()
            args = []
            conditional = False
            for expr in decompiler:
                line = str(expr)
                if 'read16' in line:
                    args.append(2)
                    if '    ' in line:
                        conditional = True
                elif 'read32' in line:
                    args.append(4)
                    if '    ' in line:
                        conditional = True
                elif 'engine.ram.set_word(engine.vars.state+8,' in line:
                    args.append(1)
                    if '    ' in line:
                        conditional = True
            try:
                if old_commands[i].__class__.__name__ != 'Command':
                    continue
                if old_commands[i].args == args:
                    continue
            except:
                pass
            commands[i] = {
                'args': args,
            }
            if conditional:
                commands[i]['conditional'] = True
        print('skipped', skip)

    with open(os.path.join(target_game.files.directory, 'commands.json'), 'w')\
            as handle:
        json.dump(commands, handle, indent=2, sort_keys=True)
