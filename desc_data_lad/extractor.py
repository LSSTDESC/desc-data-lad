from os.path import join as opj
import logging

lgr = logging.getLogger("desc_data_lad.extractor")
from datalad.log import log_progress

from datalad.metadata.extractors.base import BaseMetadataExtractor
from datalad.support.exceptions import CapturedException
import h5py


keys = [
    "config/name",
    "creation",
    "domain",
    "username",
    "uuid",
    "githead",
]


def get_metadata_from_desc_file(filename):
    meta = {}

    # This is an example of how we get metadata from TXPipe HDF5 files
    # We could add a bunch of other options here for different file
    # types.
    with h5py.File(f, "r") as fh:
        d = dict(fh["provenance/"].attrs)
        for k in keys:
            v = d.get(k, "UNKNOWN")
            if k == "config/name":
                k = "stage_name"
            meta[k] = v
    return meta


class MetadataExtractor(BaseMetadataExtractor):
    def get_metadata(self, dataset, content):
        if not content:
            return {}, []

        log_progress(
            lgr.info,
            "extractordesc",
            "Start DESC metadata extraction from %s",
            self.ds,
            total=len(self.paths),
            label="desc metadata extraction",
            unit=" Files",
        )

        content_meta = []
        for f in self.paths:
            if not f.endswith("hdf5"):
                continue

            log_progress(
                lgr.info,
                "extractordesc",
                "Extract DESC metadata from %s",
                f,
                update=1,
                increment=True,
            )
            try:
                meta = get_metadata_from_desc_file(f)
            except Exception as e:
                lgr.debug(
                    "DESC metadata extractor failed to load %s: %s",
                    f,
                    CapturedException(e),
                )
                continue

            content_meta.append((f, meta))

        log_progress(
            lgr.info,
            "extractordesc",
            "Finished DESC metadata extraction from %s",
            self.ds,
        )

        return None, content_meta
