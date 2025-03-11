from pymediainfo import MediaInfo


def getMetadataVideoFile(pathfile: str):

    media_info = MediaInfo.parse(pathfile)

    metadata = {}
    for track in media_info.tracks:
        if track.track_type == "Video":
            metadata["Format"] = track.format
            metadata["Duration"] = track.duration
            metadata["Width"] = track.width
            metadata["Height"] = track.height
            metadata["FPS"] = track.frame_rate
            metadata["Frame_count"] = track.frame_count
            metadata['Scan_type'] = track.scan_type
            metadata['Language'] = track.language
    return metadata
