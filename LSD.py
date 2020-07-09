import ffmpeg, json
from os.path import splitext as splitpath
from gooey import Gooey
from gooey import GooeyParser

codec_list = \
[
'aac',
'ac3',
'libopencore_amrnb',
'libvo_amrwbenc',
'eac3',
'g723_1',
'mp2',
'mp3',
'libopus',
'real_144',
'speex',
'libvorbis',
]

bitrate_lower_limit = \
{
'aac': 4,
'ac3': 4,
'libopencore_amrnb': 4,
'libvo_amrwbenc': 4,
'eac3': 4,
'g723_1': 6.3,
'mp2': 32,
'mp3': 4,
'libopus': 4,
'real_144': 8,
'speex': 4,
'libvorbis': 48,
}

output_fmt = \
{
'aac': 'nut',
'ac3': 'nut',
'libopencore_amrnb': 'nut',
'libvo_amrwbenc': 'nut',
'eac3': 'nut',
'g723_1': 'nut',
'mp2': 'nut',
'mp3': 'nut',
'libopus': 'nut',
'real_144': 'rm',
'speex': 'nut',
'libvorbis': 'nut',
}

required_opts = \
{
'libopencore_amrnb':    {'ar':'8k','ac':1},
'libvo_amrwbenc':       {'ar':'16k','ac':1},
'g723_1':               {'ar':'8k','ac':1}
}
args = None

@Gooey
def main():
    parser = GooeyParser(description="Lossy Sound Destroyer")
    parser.add_argument('filepath', type=str, help='the input file', widget='FileChooser')
    parser.add_argument('codec', type=str, help='the name of the codec to use', choices=codec_list)
    parser.add_argument('bitrate', type=int, help='the desired bitrate (not guaranteed)')
    parser.add_argument('glitch', type=int, help='amount to glitch (1 is a lot, 10000 is not, 0 is none)')
    args = parser.parse_args()
    
    doRoundtrip(args.filepath, args.codec, args.bitrate, args.glitch)
    
       

def doRoundtrip(filepath, codec, bitrate, glitch):

    bitrate = bitrate if (bitrate >= bitrate_lower_limit[codec]) else bitrate_lower_limit[codec]
    fmt = output_fmt[codec]
    extraopts = None
    if (codec in required_opts):
        extraopts = required_opts[codec]
    
    try:
        if extraopts is not None:
            encoded, _ = (
                ffmpeg
                .input(filepath)
                .output('pipe:',format=fmt,acodec=codec,audio_bitrate=str(bitrate)+'k',**{'bsf': f"noise={glitch}"},**extraopts)
                .global_args('-hide_banner','-loglevel','error')
                .run(capture_stdout=True)
                )
        else:        
            encoded, _ = (
                ffmpeg
                .input(filepath)
                .output('pipe:',format=fmt,acodec=codec,audio_bitrate=str(bitrate)+'k',**{'bsf': f"noise={glitch}"})
                .global_args('-hide_banner','-loglevel','error')
                .run(capture_stdout=True)
                )
    except ffmpeg.Error as e:
        if e.stderr is not None:
            print(e.stderr)
        return
        
    newfilepath = splitpath(filepath)[0] + "_" + codec + "_" + str(bitrate) + "k_" + str(glitch) + ".wav"
    
    decoded, _ = (
        ffmpeg
        .input('pipe:')
        .output(newfilepath)
        .global_args('-hide_banner','-loglevel','0','-y')
        .run(input=encoded, capture_stdout=True)
        )

if __name__ == '__main__':
    main()