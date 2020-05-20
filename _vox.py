import numpy as np 
from random import randint


def ReadVoxs( path ):
    
    with open(path, 'rb') as voxfile:
        # read size
        dimbytes = voxfile.read(12)
        dimx = int.from_bytes( dimbytes[0:4], byteorder='little' )
        dimy = int.from_bytes( dimbytes[4:8], byteorder='little' )
        dimz = int.from_bytes( dimbytes[8:12], byteorder='little' )

        voxbytes = voxfile.read( dimx*dimy*dimz )
        voxs = np.zeros((dimz, dimy, dimx), dtype=int)

        idx = 0
        for i in range(dimx-1, -1, -1):
            for j in range(dimy):
                for k in range(dimz-1, -1, -1):
                    voxs[k][j][i] = voxbytes[idx]
                    idx += 1

        return voxs     

def SaveVoxs( path, voxs, palette ):

    dimz, dimy, dimx = voxs.shape

    with open(path, "wb") as outfile:
        outfile.write((dimx).to_bytes(length=4, byteorder='little'))
        outfile.write((dimy).to_bytes(length=4, byteorder='little'))
        outfile.write((dimz).to_bytes(length=4, byteorder='little'))

        for i in range(dimx-1, -1, -1):
            for j in range(dimy):
                for k in range(dimz-1, -1, -1):
                    outfile.write( int( voxs[k][j][i] ).to_bytes(length=1, byteorder='little') )

        for col in palette:
            for val in col:
                outfile.write( int(val).to_bytes(length=1, byteorder='little') )

def CreatePalette():
    palette = np.zeros((256,3), dtype=int)
    # palette[123][:] = (127, 0, 127)
    # palette[124][:] = (255, 0, 0)
    # palette[125][:] = (0, 255, 0)
    # palette[126][:] = (0, 0, 255)
    # palette[127][:] = (255, 255, 255)
    for i in range(255):
        palette[i][:] = (randint(0,255),randint(0,255),randint(0,255))
    return palette