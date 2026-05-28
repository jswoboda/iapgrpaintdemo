# iapgrpaintdemo
MIT Haystack GR-Paint Demo 
We originally made this for tours during Independent Activities Period (IAP) at MIT.


## Theory of Operation
The multimagepaint.grc file is a gnuradio script that outputs a 6 MHz wide transmission, centered at 915 MHz, of three different images with [GR-Paint](https://github.com/drmpeg/gr-paint) `spectrum painter` block. Each spectrum painter stream at 2 MHz is then placed into a polyphase synthesizer to be transmitted over different frequencies. SDRs with narrow bandwidths (~2 MHz) can then tune to view individual pictures. The current set up uses a ADALM Pluto but differnet radio sinks can be used, just make sure the SDR can handle the bandwidth. 

Currently three images are stitched together and need to be black and white bin files. These files can be made by first creating a tga image and then using tgatoluma. The next section will detail how to translate the images. There is a gnuradio-block that comes with GR-Paint to read the images for input to the spectrum painter blockformat. There were some issues in the past with using this block on a Mac, likely due to the legendary conversion from x86 to ARM of the late 2010s-2020s.  

## Translating an image
Images can be augmented by using tools like [ImageMagick](https://imagemagick.org/#gsc.tab=0). Its suggest the user start with a png. Keep in mind how the waterfall viewer operates if the viewer is rising from the bottom of the page then image will need to be flipped. Imagemagick can be used:

``` bash
magick <inputimage> -flip <flippedimage>
# or
flip  <inputimage> <flippedimage>
```

A black and white image is needed so a tga file is needed. 

``` bash
magick <inputimage> <tgaimage>
# or
convert  <inputimage> <tgaimage>
```

Lastly to create the bin file tagtoluma.c is included in the directory. It builds with gcc and then can be used:

``` bash
gcc -o tgaotuma tgatoluma.c
tgaotuma <tgaimage> <binimage>
```

## Testing
Open gnuradio companion and open the grc file.

```bash

gnuradio-companion
````

This will allow you to augment the code in the visual gnuradio companion enviornment. 

Alternatively if the Pluto is plugged in you can just run the python program 

```bash
python iapgrpaintdemo.py
```

In a seperate terminal open up gqrx and connect an RTL-SDR. Tune around 915 MHz +/- a MHz or two in order to see pictures. In the GQRX rx window adjust the gain until the images are apparent in the waterfall. 

Make sure flip IQ is not activated as it will cause the images will be horizontally flipped int the waterfall. IQ balence should also be selected, if not images from other pictures can appear in the waterfall.
