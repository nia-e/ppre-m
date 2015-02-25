
from compileengine.assembler import Disassembler


class Thumb(Disassembler):
    stack = []

    @staticmethod
    def get_regs(data):
        regs = []
        for i in range(16):
            if data & (1 << i):
                regs.append('r{0}'.format(i))
        return regs

    @staticmethod
    def get_reg(data, high=False):
        if high:
            data += 8
        if data == 14:
            return 'lr'
        return 'r{0}'.format(data)

    @staticmethod
    def sign(value, bits):
        opp = 1 << bits
        if value & (opp >> 1):
            value -= opp
        return value

    def parse_next(self):
        cmd = self.read_value(2)
        if cmd & 0b1111011000000000 == 0b1011010000000000:
            regs = self.get_regs(cmd & 0x7F)
            if cmd & 0x800:
                func = 'pop'
                if cmd & 0x100:
                    regs.append('pc')
            else:
                func = 'push'
                if cmd & 0x100:
                    regs.append('lr')
            return [self.build(func, *regs)]
        elif cmd & 0b1111100000000000 == 0b1110000000000000:
            # b
            self.seek(self.tell()+(cmd & 0x3FF))
            return []
        elif cmd & 0b1111000000000000 == 0b1111000000000000:
            # bl
            ofs = (cmd & 0x7FF) << 12
            ofs += (self.read_value(2) & 0x7FF) << 1
            ofs = self.sign(ofs, 23) + self.tell()
            return [self.build('bl', ofs)]
        elif cmd & 0b1111111100000000 == 0b0100011100000000:
            # bx
            reg = self.get_reg((cmd >> 3) & 0x7, cmd & 0x40)
            if reg == 'lr':
                return [self.end()]
            return [self.build('bx', reg)]
        else:
            return [self.unknown(cmd)]
