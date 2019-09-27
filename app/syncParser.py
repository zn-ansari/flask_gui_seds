import struct

class Parser:
    SYNC_WORD = b"\xdb\x69\xc0\x78"
    PKT_LEN = 40
    FLIGHT_PHASES = [
        "Startup",
        "Idle",
        "Launched",
        "DescendingWithDrogue",
        "DescendingWithMain",
        "Landed"
    ]

    def __init__(self):
        self.buf = bytes()
        self.have_sync = False
        self.sync_idx = 0

    def parse(self, data):
        """
        Adds `data`to the parser and returns any new packets that
        it finds in the data that has been added so far.
        """

        # Add the data to the end of the buffer
        self.buf += data

        # Make sure we're synced first
        if not self.have_sync and not self.sync():
            return []

        packets = []

        # Parse packets as long as there is space for another packet in the buffer
        while len(self.buf) >= self.sync_idx + self.PKT_LEN:

            # Ignore additional sync words since we're already synced
            first_word = self.buf[self.sync_idx:self.sync_idx + 4]
            if first_word == self.SYNC_WORD:
                self.sync_idx += 4
                continue

            # Pull the next packet out of the buffer
            pkt_bytes = self.buf[self.sync_idx:self.sync_idx + self.PKT_LEN]
            self.sync_idx += self.PKT_LEN
            (temp, millis, alt, vel, acc, raw_alt, raw_acc, lat, lon, batt_mv, phase, cksum) = struct.unpack("<iIfffffffHBB", pkt_bytes)

            # Reset sync if we get an invalid packet
            if phase >= len(self.FLIGHT_PHASES) or temp > 100000 or not self.checksum(pkt_bytes[:self.PKT_LEN-1], cksum):
                print("invalid packet")
                self.have_sync = False
                self.sync()
                continue

            packets.append({
                "temp": temp / 100,  # Convert to Celsius
                "millis": millis,
                "alt": alt,
                "vel": vel,
                "acc": acc,
                "raw_alt": raw_alt,
                "raw_acc": raw_acc,
                "lat": lat,
                "lon": lon,
                "batt_v": batt_mv / 1000,  # Convert from mV to V
                "phase": self.FLIGHT_PHASES[phase]
            })

        # Now remove all of the data from the buffer that has already been parsed
        self.buf = self.buf[self.sync_idx:]
        self.sync_idx = 0

        return packets

    def checksum(self, pkt_bytes, cksum):
        for b in pkt_bytes:
            cksum ^= b
        return cksum == 0

    def sync(self):
        idx = self.buf.find(self.SYNC_WORD)
        if idx == -1:
            return False

        # Throw away the sync word and everything before it
        # and set our sync to the start of the buffer.
        self.buf = self.buf[idx + 4:]
        self.sync_idx = 0
        self.have_sync = True
        return True

# import struct

# class Parser:
#     SYNC_WORD = b"\xdb\x69\xc0\x78"
#     PKT_LEN = 39
#     FLIGHT_PHASES = [
#         "Startup",
#         "Idle",
#         "Launched",
#         "DescendingWithDrogue",
#         "DescendingWithMain",
#         "Landed"
#     ]

#     def __init__(self):
#         self.buf = bytes()
#         self.have_sync = False
#         self.sync_idx = 0

#     def parse(self, data):
#         """
#         Adds `data`to the parser and returns any new packets that
#         it finds in the data that has been added so far.
#         """

#         # Add the data to the end of the buffer
#         self.buf += data

#         # Make sure we're synced first
#         if not self.have_sync:
#             if not self.sync():
#                 return []

#         packets = []

#         # Parse packets as long as there is space for another packet in the buffer
#         while len(self.buf) > self.sync_idx + self.PKT_LEN:

#             # Ignore additional sync words since we're already synced
#             first_word = self.buf[self.sync_idx:self.sync_idx + 4]
#             if first_word == self.SYNC_WORD:
#                 self.sync_idx += 4
#                 continue

#             # Pull the next packet out of the buffer
#             pkt_bytes = self.buf[self.sync_idx:self.sync_idx + self.PKT_LEN]
#             self.sync_idx += self.PKT_LEN
#             (temp, millis, alt, vel, acc, raw_alt, raw_acc, lat, lon, batt_mv, phase) = struct.unpack("<iIfffffffHB", pkt_bytes)

#             # Reset sync if we get an invalid packet
#             if phase >= len(self.FLIGHT_PHASES) or temp > 100000:
#                 self.have_sync = False
#                 if self.sync():
#                     continue
#                 else :
#                     break


#             packets.append({
#                 "temp": temp / 100,  # Convert to Celsius
#                 "millis": millis,
#                 "alt": alt,
#                 "vel": vel,
#                 "acc": acc,
#                 "raw_alt": raw_alt,
#                 "raw_acc": raw_acc,
#                 "lat": lat,
#                 "lon": lon,
#                 "batt_v": batt_mv / 1000,  # Convert from mV to V
#                 "phase": self.FLIGHT_PHASES[phase]
#             })

#         # Now remove all of the data from the buffer that has already been parsed
#         self.buf = self.buf[self.sync_idx:]
#         self.sync_idx = 0

#         return packets

#     def sync(self):
#         idx = self.buf.find(self.SYNC_WORD)
#         if idx == -1:
#             return False

#         # Throw away the sync word and everything before it
#         # and set our sync to the start of the buffer.
#         self.buf = self.buf[idx + 4:]
#         self.sync_idx = 0
#         self.have_sync = True
#         return True
