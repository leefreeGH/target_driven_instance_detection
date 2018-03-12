# Target Driven Instance Detection

This is an implementation of the technique described in "Target Driven Instance Detection". It is written in python for use with Pytorch. 


## External Requirements
* Python 2 (might work with Python 3)
* [PyTorch](http://pytorch.org/)
* [AVD Data](http://www.cs.unc.edu/~ammirato/active_vision_dataset_website/get_data.html) Parts 1, 2 and 3
* [AVD processing code](https://github.com/ammirato/active_vision_dataset_processing)

## Installation
These instructions will setup the code and data to run our experiments on the AVD dataset. More instructions will be provided to run our other experiments or use your own data.  

0. Dependencies and Data:

- Make sure you have Pytorch (and torchvision)
- Get the [AVD processing code](https://github.com/ammirato/active_vision_dataset_processing), and make sure it is included in your PYTHONPATH
- Download the [AVD Data](http://www.cs.unc.edu/~ammirato/active_vision_dataset_website/get_data.html) into a path of your choosing, we will refer to is as `AVD_ROOT_DIR`.
- Download the [target images](https://drive.google.com/file/d/1uV2I-SYWQvJb0PqzDdg8ESwRdQoVpSWr/view?usp=sharing) into a path of your choosing, we will refer to is as `TARGET_IMAGE_DIR`.

1. Get the code
```
git clone https://github.com/ammirato/target_driven_instance_detection.git
```

2. Install the other requirements
```
cd target_driven_instance_detection/
pip install -r requirements.txt
```

3. Build the cython code for anchor boxes and non-max supression
```
cd model_defs/
./make.sh
```

4. Build the coco evaluation cython code 
```
cd ../evaluation/cocoapi/PythonAPI/
make all
cd ../../../
```

5. Convert AVD annotations to COCO format yourself, or download the converted files

**To Download the files:**
```
mkdir Data
cd Data
``` 

Download the tar [here](https://drive.google.com/file/d/1VgDBR5K1I-Tb6QVqyqVfGEXxcwKGHjQx/view?usp=sharing) 

`tar -xf tdid_gt_boxes.tar`

**Or to convert yourself:**
```python
cd  evaluation/
#Update paths in `convert_AVDgt_to_COCOgt.py` with:
#your AVD_ROOT_DIR
#a path to save the annotations, we will call it VAL_GROUND_TRUTH_BOXES
python convert_AVDgt_to_COCOgt.py

#now update the scene_list in convert_AVDgt_to_COCOgt.py 
#to make the test set
#change the path to save the annotations, we will call it TEST_GROUND_TRUTH_BOXES
python convert_AVDgt_to_COCOgt.py

```


6. Set paths `configs/configAVD2.py` file. See `configs/README.md` for details on config files. Make sure to update the config with your:

    - `AVD_ROOT_DIR`
    - `TARGET_IMAGE_DIR`
    - `VAL_GROUND_TRUTH_BOXES` 
    - `TEST_GROUND_TRUTH_BOXES`

7. Start training!
```
#make sure you are in root directory of project, target_driven_instance_detection/
python train_tdid.py
```



### TODO
1. Set up validation code --DONE
2. converting AVD to coco gt --DONE
3. evaling on org AVD  --DONE
4. config files
5. Add to README for extra data (target images, synthetic data)
6. Insatnce id map
7. GMU DATA things
8. UW data things
6. Fix eval by object
7. Test det4class
8. provide trained models
9. make a note about downloading pretrained pytorch models

### Acknowledgements
This code started as a modification of a Faster-RCNN Pytorch implementation [here](https://github.com/longcw/faster_rcnn_pytorch), and still uses some of that code. (In particular nothing was changed in the nms code).



