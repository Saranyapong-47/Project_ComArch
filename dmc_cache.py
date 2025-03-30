import math
import random

class DMCLine:
    def __init__(self):
        self.valid = False
        self.tag = None

# -------------------------------------------------
# 2) DirectMappedCache
# -------------------------------------------------
class DirectMappedCache:
    def __init__(self, cache_size, block_size, address_bits=32):
        self.cache_size = cache_size
        self.block_size = block_size
        self.address_bits = address_bits
        
        # คำนวณจำนวน line
        self.num_lines = max(1, cache_size // block_size)
        
        # offset bits, index bits
        self.offset_bits = int(math.log2(block_size)) if block_size > 1 else 0
        self.index_bits = int(math.log2(self.num_lines)) if self.num_lines > 1 else 0
        
        # สร้าง list ของ line
        self.lines = [DMCLine() for _ in range(self.num_lines)]
        
        # สถิติ
        self.hit_count = 0
        self.miss_count = 0
        self.access_count = 0
        
        # Log Access (address, offset, index, tag, is_hit)
        self.access_log = []

    def access(self, address):
        self.access_count += 1
        
        # คำนวณ offset, index, tag
        offset_mask = (1 << self.offset_bits) - 1 if self.offset_bits > 0 else 0
        index_mask = (1 << self.index_bits) - 1 if self.index_bits > 0 else 0
        
        offset = address & offset_mask
        index = (address >> self.offset_bits) & index_mask
        tag = address >> (self.offset_bits + self.index_bits)
        
        line = self.lines[index]
        
        # ตรวจ Hit/Miss
        is_hit = False
        if line.valid and line.tag == tag:
            is_hit = True
            self.hit_count += 1
        else:
            self.miss_count += 1
            line.valid = True
            line.tag = tag
        
        # เก็บใน access_log
        self.access_log.append((address, offset, index, tag, is_hit))

    def get_stats(self):
        if self.access_count == 0:
            return {
                'access_count': 0,
                'hit_count': 0,
                'miss_count': 0,
                'hit_rate': 0.0,
                'miss_rate': 0.0,
            }
        hit_rate = self.hit_count / self.access_count
        miss_rate = self.miss_count / self.access_count
        return {
            'access_count': self.access_count,
            'hit_count': self.hit_count,
            'miss_count': self.miss_count,
            'hit_rate': hit_rate,
            'miss_rate': miss_rate,
        }

    def reset(self):
        """ลบข้อมูลใน cache ทั้งหมด + สถิติ"""
        for line in self.lines:
            line.valid = False
            line.tag = None
        self.hit_count = 0
        self.miss_count = 0
        self.access_count = 0
        self.access_log = []

# -------------------------------------------------