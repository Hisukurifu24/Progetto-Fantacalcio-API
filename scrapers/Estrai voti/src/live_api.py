import requests
import re
import json
import math
import struct
import logging

logger = logging.getLogger(__name__)

class ProtoReader:
    def __init__(self, data):
        self.data = data
        self.pos = 0

    def read_varint(self):
        result = 0
        shift = 0
        while True:
            if self.pos >= len(self.data):
                raise EOFError("Unexpected EOF while reading varint")
            b = self.data[self.pos]
            self.pos += 1
            result |= (b & 0x7F) << shift
            if not (b & 0x80):
                return result
            shift += 7

    def read_fixed64(self):
        if self.pos + 8 > len(self.data):
            raise EOFError("Unexpected EOF")
        val = struct.unpack('<d', self.data[self.pos:self.pos+8])[0]
        self.pos += 8
        return val

    def read_string(self):
        length = self.read_varint()
        if self.pos + length > len(self.data):
            raise EOFError("Unexpected EOF")
        s = self.data[self.pos:self.pos+length].decode('utf-8', errors='ignore')
        self.pos += length
        return s

    def read_bytes(self):
        length = self.read_varint()
        if self.pos + length > len(self.data):
             raise EOFError("Unexpected EOF")
        b = self.data[self.pos:self.pos+length]
        self.pos += length
        return b
    
    def next_tag(self):
        if self.pos >= len(self.data):
            return None, None
        tag_int = self.read_varint()
        field_num = tag_int >> 3
        wire_type = tag_int & 0x07
        return field_num, wire_type

class FantacalcioLiveAPI:
    BASE_URL = "https://www.fantacalcio.it"
    API_URL = "https://api.fantacalcio.it/v1"
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
             "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
             "Origin": self.BASE_URL,
        })
        
    def _decode_descriptor(self, s, seed):
        decoded = []
        for char in s:
            code = ord(char)
            if code == 13: continue
            x = math.sin(seed) * 10000
            rnd = x - math.floor(x)
            seed += 1
            decoded_char_code = code - (math.floor(rnd * 2) - 1)
            decoded.append(chr(decoded_char_code))
        return "".join(decoded)

    def _parse_player(self, reader):
        player = {}
        while True:
            field, wire = reader.next_tag()
            if field is None: break
            
            if field == 1: player['id'] = reader.read_varint()
            elif field == 2: player['name'] = reader.read_string()
            elif field == 3: player['role'] = reader.read_string()
            elif field == 4: 
                if wire == 1: player['vote'] = reader.read_fixed64()
                else: reader.read_varint()
            else:
                self._skip_field(reader, wire)
        return player

    def _parse_protodata(self, reader):
        match_data = {'home': [], 'away': []}
        while True:
            field, wire = reader.next_tag()
            if field is None: break
            
            if field == 1: match_data['match_id'] = reader.read_varint()
            elif field == 15: match_data['home'].append(self._parse_player(ProtoReader(reader.read_bytes())))
            elif field == 16: match_data['away'].append(self._parse_player(ProtoReader(reader.read_bytes())))
            else: self._skip_field(reader, wire)
        return match_data

    def _skip_field(self, reader, wire):
        if wire == 0: reader.read_varint()
        elif wire == 1: reader.pos += 8
        elif wire == 2: reader.read_bytes()
        elif wire == 5: reader.pos += 4

    def get_live_votes(self, match_url):
        logger.info(f"Fetching live votes for: {match_url}")
        
        # 1. Fetch Page to get Bridge config
        self.session.headers["Referer"] = match_url
        r = self.session.get(match_url)
        if r.status_code != 200:
            raise Exception(f"Failed to load page: {r.status_code}")
            
        bridge_match = re.search(r'const Bridge\s*=\s*(\{.*?\})\s*', r.text, re.DOTALL)
        if not bridge_match:
             # Fallback
             bridge_match = re.search(r'Bridge\s*=\s*(\{.*?\});', r.text, re.DOTALL)
             
        if not bridge_match:
            raise Exception("Could not find Bridge configuration in HTML")
            
        json_str = bridge_match.group(1)
        
        # Extract seasonId and matchweek using regex to avoid JSON parsing issues with JS syntax
        sid_match = re.search(r'seasonId\s*:\s*["\']?([^"\',\}]+)["\']?', json_str)
        mw_match = re.search(r'matchweek\s*:\s*["\']?([^"\',\}]+)["\']?', json_str)
        mid_match = re.search(r'matchId\s*:\s*["\']?([^"\',\}]+)["\']?', json_str)
        
        if not (sid_match and mw_match and mid_match):
            raise Exception("Could not parse Bridge config values")
            
        season_id = sid_match.group(1)
        matchweek = mw_match.group(1)
        match_id = int(mid_match.group(1))
        
        logger.info(f"Bridge Config: Season={season_id}, Week={matchweek}, Match={match_id}")
        
        # 2. Get Signed URI
        resource_path = f"st/{season_id}/matches/live/{matchweek}.dat"
        # SignedUri endpoint is on WWW, not API
        uri_endpoint = f"{self.BASE_URL}/api/v1/SignedUri"
        
        payload = { "resourcesUri": [resource_path] } # Use relative path!
        # Note: In debug, I found I needed absolute URL sometimes, but API JS uses relative.
        # If relative fails, logic below should handle? No, just try relative first.
        # Actually, in my successful debug run, I passed BOTH. 
        # But the successful one was the absolute URL: `https://api.fantacalcio.it/v1/st/20/matches/live/19.dat`
        # Let's try constructing the full URL.
        full_resource_url = f"{self.API_URL}/{resource_path}"
        
        r_sign = self.session.post(uri_endpoint, json={"resourcesUri": [full_resource_url]})
        if r_sign.status_code != 200:
            logger.error(f"SignedUri failed: {r_sign.text}")
            raise Exception("Failed to get Signed URI")
            
        data = r_sign.json()
        if full_resource_url not in data or not data[full_resource_url].get('resources'):
            # Try relative path fallback
             r_sign = self.session.post(uri_endpoint, json={"resourcesUri": [resource_path]})
             data = r_sign.json()
             if resource_path not in data or not data[resource_path].get('resources'):
                 raise Exception("SignedUri resource not found in response")
             signed_uri = data[resource_path]['resources'][0]['signedUri']
        else:
             signed_uri = data[full_resource_url]['resources'][0]['signedUri']
            
        # 3. Fetch Binary Data
        logger.info("Fetching binary data...")
        r_bin = self.session.get(signed_uri)
        if r_bin.status_code != 200:
            raise Exception(f"Failed to fetch binary data: {r_bin.status_code}")
            
        # 4. Parse Data
        reader = ProtoReader(r_bin.content)
        all_matches = []
        while True:
            field, wire = reader.next_tag()
            if field is None: break
            
            if field == 1: # protoData
                p_data = reader.read_bytes()
                all_matches.append(self._parse_protodata(ProtoReader(p_data)))
            else:
                self._skip_field(reader, wire)
                
        # 5. Find specific match
        for m in all_matches:
            if m['match_id'] == match_id:
                return m
                
        return None

if __name__ == "__main__":
    # Test
    api = FantacalcioLiveAPI()
    try:
        url = "https://www.fantacalcio.it/serie-a/calendario/19/2025-26/lecce-roma/16854/voti"
        data = api.get_live_votes(url)
        print(json.dumps(data, indent=2))
    except Exception as e:
        print(f"Error: {e}")
