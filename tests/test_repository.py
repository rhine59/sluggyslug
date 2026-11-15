"""Repository boundaries: private runtime state and bulk photos must not be tracked."""
import unittest,subprocess,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
class RepositoryTests(unittest.TestCase):
 def test_no_private_state_tracked(self):
  paths=subprocess.check_output(['git','-C',str(ROOT),'ls-files','-z']).decode().split('\0')
  bad=[p for p in paths if Path(p).name in {'.env','session-key','setup-token'} or Path(p).suffix in {'.pem','.key','.sqlite','.sqlite3'}]
  self.assertEqual(bad,[])
 def test_bulk_photos_excluded(self):
  manifest=ROOT/'reports/nas-media-manifest.json'
  if not manifest.exists():self.skipTest('Media manifest not checked out')
  paths=set(subprocess.check_output(['git','-C',str(ROOT),'ls-files','-z']).decode().split('\0'))
  omitted=json.loads(manifest.read_text());unexpected=['website/'+kind+'/'+x['path'] for kind,rows in omitted.items() for x in rows if 'website/'+kind+'/'+x['path'] in paths]
  self.assertEqual(unexpected,[])
