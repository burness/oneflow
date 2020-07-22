import numpy as np
import oneflow as flow

DATA_DIR = "/dataset/imagenet_16_same_pics/ofrecord"

flow.config.gpu_device_num(1)

func_config = flow.FunctionConfig()
func_config.default_distribute_strategy(flow.scope.consistent_view())
func_config.default_data_type(flow.float)


@flow.global_function(func_config)
def DataLoaderJob():
    batch_size = 8
    seed = 0
    rgb_mean = [123.68, 116.779, 103.939]
    rgb_std = [58.393, 57.12, 57.375]

    ofrecord = flow.data.ofrecord_loader(DATA_DIR, batch_size=batch_size)
    image = flow.data.OFRecordImageDecoderRandomCrop(
        ofrecord, "encoded", seed=seed, color_space="RGB"
    )
    label = flow.data.OFRecordRawDecoder(
        ofrecord, "class/label", shape=(), dtype=flow.int32
    )
    rsz, _ = flow.image.Resize(image, (224, 224), channels=3, interpolation="bilinear")
    print(rsz.shape)
    print(label.shape)

    rng = flow.random.CoinFlip(batch_size=batch_size, seed=seed)
    normal = flow.image.CropMirrorNormalize(
        rsz,
        mirror_blob=rng,
        color_space="RGB",
        mean=rgb_mean,
        std=rgb_std,
        output_dtype=flow.float,
    )
    print(normal.shape)
    return rsz, normal, label, rng


@flow.global_function(func_config)
def DataLoaderEvalJob():
    batch_size = 8
    rgb_mean = [123.68, 116.779, 103.939]
    rgb_std = [58.393, 57.12, 57.375]

    ofrecord = flow.data.ofrecord_loader(
        DATA_DIR,
        batch_size=batch_size,
        part_name_suffix_length=5,
        data_part_num=1,
        shuffle=False,
    )
    image = flow.data.OFRecordImageDecoder(ofrecord, "encoded", color_space="RGB")
    label = flow.data.OFRecordRawDecoder(
        ofrecord, "class/label", shape=(), dtype=flow.int32
    )
    rsz, _, _ = flow.image.target_resize(image, target_size=256)

    normal = flow.image.CropMirrorNormalize(
        rsz,
        color_space="RGB",
        crop_h=224,
        crop_w=224,
        crop_pos_y=0.5,
        crop_pos_x=0.5,
        mean=rgb_mean,
        std=rgb_std,
        output_dtype=flow.float,
    )
    return normal, label


if __name__ == "__main__":
    rsz, normal, label, rng = DataLoaderJob().get()
    print("resized image: ", rsz)
    print("normalized image output: ", normal)
    print("label: ", label)
    print("mirror:", rng)
    np.save("output/oneflow_train_data_0.npy", normal.numpy())

    rsz, normal, label, rng = DataLoaderJob().get()
    print("resized image: ", rsz)
    print("normalized image output: ", normal)
    print("label: ", label)
    print("mirror:", rng)
    np.save("output/oneflow_train_data_1.npy", normal.numpy())

    normal, label = DataLoaderEvalJob().get()
    print("normalized image output: ", normal)
    print("label: ", label)
    np.save("output/oneflow_eval_data_0.npy", normal.numpy())
