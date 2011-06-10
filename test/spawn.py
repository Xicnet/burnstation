
import os

cmd = "../scripts/burn"
args = [cmd, '-A', '-a', '/usr/local/media/music/Costellam/cll003_electroputas_electroputas/[cll003]_03_electroputas__De_La_Isla.ogg']
b = os.spawnvpe(os.P_NOWAIT, cmd, args, os.environ)

