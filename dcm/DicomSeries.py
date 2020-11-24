#### ##     ## ########   #######  ########  ########  ######
 ##  ###   ### ##     ## ##     ## ##     ##    ##    ##    ##
 ##  #### #### ##     ## ##     ## ##     ##    ##    ##
 ##  ## ### ## ########  ##     ## ########     ##     ######
 ##  ##     ## ##        ##     ## ##   ##      ##          ##
 ##  ##     ## ##        ##     ## ##    ##     ##    ##    ##
#### ##     ## ##         #######  ##     ##    ##     ######

# Standard
import sys, gc

# DICOM
if sys.version < "3":
    import dicom
    from dicom.sequence import Sequence
else:
    from pydicom import dicomio as dicom
    from pydicom.sequence import Sequence

# Domain
from domain.Node import Node

from dcm.DSRDocument import DSRDocument
from dcm.DicomRtStructure import DicomRtStructure


class DicomSeries(Node):
    """DicomSeries
    This class represents a serie of dicom files that belong together.
    If these are multiple files, they represent the slices of a volume
    (like for CT or MRI). The actual volume can be obtained using loadData().
    Information about the data can be obtained using the info attribute.
    """

    # To create a DicomSeries object, start by making an instance and
    # append files using the "_append" method. When all files are
    # added, call "_sort" to sort the files, and then "_finish" to evaluate
    # the data, perform some checks, and set the shape and sampling
    # attributes of the instance.

    def __init__(self, suid, showProgress=False, parent=None):
        """Default constructor
        """
        super(DicomSeries, self).__init__(suid, parent)

        # Init dataset list and the callback
        self._datasets = Sequence()
        self._showProgress = showProgress

        # Init properties
        self._suid = suid
        self._modality = ""
        self._info = None
        self._shape = None
        self._sampling = None
        self._description = ""
        self._newDescription = ""
        self._date = ""
        self._time = ""

        self._studyInstanceUid = None
        self._files = []
        self._dsrDocuments = []
        self._approvedReportText = ""
        self._isApproved = False

########  ########   #######  ########  ######## ########  ######## #### ########  ######
##     ## ##     ## ##     ## ##     ## ##       ##     ##    ##     ##  ##       ##    ##
##     ## ##     ## ##     ## ##     ## ##       ##     ##    ##     ##  ##       ##
########  ########  ##     ## ########  ######   ########     ##     ##  ######    ######
##        ##   ##   ##     ## ##        ##       ##   ##      ##     ##  ##             ##
##        ##    ##  ##     ## ##        ##       ##    ##     ##     ##  ##       ##    ##
##        ##     ##  #######  ##        ######## ##     ##    ##    #### ########  ######

    @property
    def name(self):
        """Overwrite name to display reasonable info about the DICOM series
        """
        if self.modality == "RTSTRUCT":
            return "[" + self.modality + "] " + self.description + " <ROI=" + str(self.objects) + ">" + " (" + str(self.size) + ")"
        else:
            return "[" + self.modality + "] " + self.description + " (" + str(self.size) + ")"

    @property
    def suid(self):
        """ SeriesInstanceUID Getter"""
        return self._suid

    @property
    def shape(self):
        """ The shape of the data (nz, ny, nx).
        If None, the serie contains a single DICOM file
        """
        return self._shape

    @property
    def sampling(self):
        """ The sampling (voxel distances) of the data (dz, dy, dx).
        If None, the serie contains a single DICOM file
        """
        return self._sampling

    @property
    def info(self):
        """ A DataSet instance containing the information as present in the
        first DICOM file of this serie
        """
        return self._info

    @property
    def description(self):
        """DICOM series description Getter (supports DICOM-RT modalities)
        """
        result = ""

        # One of these can have interesting data to display
        # (RTPlanLabel, RTPlanName, RTPlanDescription)
        # TODO: PrescriptionDescription - can be intereting to display somewhere
        if self.modality == "RTPLAN":
            if self._datasets:
                if "RTPlanLabel" in self._datasets[0] and self._datasets[0].RTPlanLabel != "":
                    result = self._datasets[0].RTPlanLabel
                elif "RTPlanName" in self._datasets[0] and self._datasets[0].RTPlanName != "":
                    result = self._datasets[0].RTPlanName
                elif "RTPlanDescription" in self._datasets[0] and self._datasets[0].RTPlanDescription != "":
                    result = self._datasets[0].RTPlanDescription
        
        # One of these can have insteresting data to display
        # (DoseComment)
        # TODO: DoseUnits   "GY", "RELATIVE"
        #       DoseType    "PHYSICAL", "EFFECTIVE, ERROR"
        elif self.modality == "RTDOSE":
            if self._datasets:
                if "DoseComment" in self._datasets[0] and self._datasets[0].DoseComment != "":
                    result = self._datasets[0].DoseComment

        # One of these can have interesting data to display
        # (StructureSetLabel, StructureSetName, StructureSetDescription)
        elif self.modality == "RTSTRUCT":
            if self._datasets:
                if "StructureSetLabel" in self._datasets[0] and self._datasets[0].StructureSetLabel != "":
                    result = self._datasets[0].StructureSetLabel
                
                # It can be usefull to display both lable and name
                if "StructureSetName" in self._datasets[0] and self._datasets[0].StructureSetName != "":
                    if result != "":
                        result += " "
                    result += self._datasets[0].StructureSetName
                elif "StructureSetDescription" in self._datasets[0] and self._datasets[0].StructureSetDescription != "":
                    if result != "":
                        result += " "
                    result += self._datasets[0].StructureSetDescription

        # One of these can have interesting data to display
        # (RTImageName, RTImageLabel, RTImageDescription)
        elif self.modality == "RTIMAGE":
            if self._datasets:
                if "RTImageName" in self._datasets and self.datasets[0].RTImageName != "":
                    result = self.datasets[0].RTImageName
                elif "RTImageLabel" in self._datasets and self.datasets[0].RTImageLabel != "":
                    result = self.datasets[0].RTImageLabel               
                elif "RTImageDescription" in self._datasets and self.datasets[0].RTImageDescription != "":
                    result = self.datasets[0].RTImageDescription

        # Append series description
        if self.info is not None:
            if "SeriesDescription" in self.info:
                if result != "":
                    result += " "
                result += self.info.SeriesDescription
        elif self._datasets:
            if "SeriesDescription" in self._datasets[0]:
                if result != "":
                    result += " "
                result += self._datasets[0].SeriesDescription

        if self._description != "" and self._description is not None:
            return self._description

        return result

    @description.setter
    def description(self, value):
        """DICOM series description Setter
        """
        self._description = value

    @property
    def modality(self):
        """DICOM series modality Getter
        """
        if self.info is not None:
            if "Modality" in self.info:
                return self.info.Modality
        
        if self._datasets:
            if "Modality" in self._datasets[0]:
                return self._datasets[0].Modality

        if self._modality != "" and self._modality is not None:
            return self._modality

        return "Not specified modality"

    @modality.setter
    def modality(self, value):
        """DICOM series modality Setter
        """
        self._modality = value

    @property
    def studyInstanceUid(self):
        """StudyInstanceUID Getter
        """
        return self._studyInstanceUid

    @property
    def newDescription(self):
        """New DICOM series description Getter
        """
        return self._newDescription

    @newDescription.setter
    def newDescription(self, value):
        """New DICOM series description Setter
        """
        self._newDescription = value

    @property
    def date(self):
        """DICOM series date Getter (supports DICOM-RT modalities)
        """
        if self._date is None or self._date == "":
            if self._datasets:
                if self.modality == "RTSTRUCT":
                    if "StructureSetDate" in self._datasets[0]:
                        self._date = self._datasets[0].StructureSetDate
                elif self.modality == "RTPLAN":
                    if "RTPlanDate" in self._datasets[0]:
                        self.date = self._datasets[0].RTPlanDate
                elif self.modality == "RTDOSE":
                    if "InstanceCreationDate" in self._datasets[0]:
                        self.date = self._datasets[0].InstanceCreationDate
                elif self.modality == "RTIMAGE":
                    if "InstanceCreationDate" in self._datasets[0]:
                        self.date = self._datasets[0].InstanceCreationDate
                elif "SeriesDate" in self._datasets[0]:
                    self._date = self._datasets[0].SeriesDate

        return self._date

    @date.setter
    def date(self, value):
        """DICOM series date Setter
        """
        self._date = value

    @property 
    def time(self):
        """DICOM series time Getter
        """
        return self._time

    @time.setter
    def time(self, value):
        """DICOM series time Setter
        """
        self._time = value

    @property
    def sopInstanceUid(self):
        """DICOM SOP instance UID of series when there is just one instance
        """
        if len(self._datasets) == 1:
            if "SOPInstanceUID" in self._datasets[0]:
                return self._datasets[0].SOPInstanceUID

    @property
    def datasets(self):
        """DICOM serie data files Getter
        """
        return self._datasets

    @property
    def files(self):
        """DICOM files
        """
        return self._files

    @property
    def size(self):
        """Number of DICOM files are in the series
        """
        return len(self._files)

    @property
    def objects(self):
        """
        """
        result = 0

        # For RTSTRUCT I want to know how many ROIs are present
        if self.modality == "RTSTRUCT":
            if self._datasets:

                # Display also count of roi structures
                roiCount = 0
                for element in self._datasets[0]:
                    if element.VR == "SQ":
                        if element.name == "Structure Set ROI Sequence":
                            for subElem in element:
                                roiCount += 1
                result = roiCount

        # For RTPLAN
        #if self.modality == "RTPLAN":
        #   if self._datasets:
        #       lines = ["{name:^13s} {num:^8s} {gantry:^8s} {ssd:^11s}".format(name="Beam name", num="Number", gantry="Gantry", ssd="SSD (cm)")]
        #           for beam in self._datasets[0].BeamSequence:
        #               cp0 = beam.ControlPointSequence[0]
        #               SSD = float(cp0.SourcetoSurfaceDistance / 10)
        #               lines.append("{b.BeamName:^13s} {b.BeamNumber:8d} "
        #                           "{gantry:8.1f} {ssd:8.1f}".format(b=beam, gantry=cp0.GantryAngle, ssd=SSD))

        return result

    @property
    def dsrDocuments(self):
        """DSR Document Getter
        """
        if self.modality == "SR":
            if len(self._dsrDocuments) == 0:
                for f in self._files:               
                    dcmFile = dicom.read_file(f, force=True)
                    self._dsrDocuments.append(DSRDocument(dcmFile))

        return self._dsrDocuments

    @property
    def approvedReportText(self):
        if self._isApproved:
            return self._approvedReportText
        else:
            return ""

    @approvedReportText.setter
    def approvedReportText(self, value):
        self._approvedReportText = value

    @property
    def isApproved(self):
        return self._isApproved

    @isApproved.setter
    def isApproved(self, value):
        self._isApproved = value

##     ## ######## ######## ##     ##  #######  ########   ######
###   ### ##          ##    ##     ## ##     ## ##     ## ##    ##
#### #### ##          ##    ##     ## ##     ## ##     ## ##
## ### ## ######      ##    ######### ##     ## ##     ##  ######
##     ## ##          ##    ##     ## ##     ## ##     ##       ##
##     ## ##          ##    ##     ## ##     ## ##     ## ##    ##
##     ## ########    ##    ##     ##  #######  ########   ######

    def typeInfo(self):
        """Display information about DICOM series as hierarchy node type
        """
        return "SERIE"

    def typeDate(self):
        """Display information about DICOM series date
        """
        return self.date

    def get_pixel_array(self):
        """ get_pixel_array()

        Get (load) the data that this DicomSeries represents, and return
        it as a numpy array. If this serie contains multiple images, the
        resulting array is 3D, otherwise it's 2D.

        If RescaleSlope and RescaleIntercept are present in the dicom info,
        the data is rescaled using these parameters. The data type is chosen
        depending on the range of the (rescaled) data
        """

        # Can we do this?
        if not have_numpy:
            msg = "The Numpy package is required to use get_pixel_array.\n"
            raise ImportError(msg)

        # It's easy if no file or if just a single file
        if len(self._datasets) == 0:
            raise ValueError('Serie does not contain any files.')
        elif len(self._datasets) == 1:
            ds = self._datasets[0]
            slice = _getPixelDataFromDataset(ds)
            return slice

        # Check info
        if self.info is None:
            raise RuntimeError("Cannot return volume if series not finished.")

        # Set callback to update progress
        showProgress = self._showProgress

        # Init data (using what the dicom packaged produces as a reference)
        ds = self._datasets[0]
        slice = _getPixelDataFromDataset(ds)
        # vol = Aarray(self.shape, self.sampling, fill=0, dtype=slice.dtype)
        vol = np.zeros(self.shape, dtype=slice.dtype)
        vol[0] = slice

        # Fill volume
        showProgress('Loading data:')
        ll = self.shape[0]
        for z in range(1, ll):
            ds = self._datasets[z]
            vol[z] = _getPixelDataFromDataset(ds)
            showProgress(float(z) / ll)

        # Finish
        showProgress(None)

        # Done
        gc.collect()
        return vol

    def appendFile(self, filename):
        """Add file (instance) to the series
        """
        self._files.append(filename)

    def documentsAreApproved(self):
        """Check if all documents are approved
        """
        for doc in self._dsrDocuments:
            if not doc.isApproved:
                return False

        return True

    def prepareRois(self):
        """
        """
        if self.modality == "RTSTRUCT":
            if len(self._children) == 0:
                if len(self._datasets) == 1:

                    for element in self._datasets[0]:
                        if element.VR == "SQ":
                            if element.name == "Structure Set ROI Sequence":
                                for subElem in element:
                                    self._children.append(
                                        DicomRtStructure(
                                            subElem.ROINumber,
                                            subElem.ROIName
                                        )
                                    )
                    if len(self._children) > 0:
                        for element in self._datasets[0]:
                            if element.VR == "SQ":
                                if element.name == "RT ROI Observations Sequence":
                                    for subElem in element:
                                        for roi in self._children:
                                            if subElem.ReferencedROINumber == roi.roiNumber:
                                                roi.roiObservationLabel = subElem.ROIObservationLabel
                                                roi.rtRoiInterpretedType = subElem.RTROIInterpretedType

########  ########  #### ##     ##    ###    ######## ######## 
##     ## ##     ##  ##  ##     ##   ## ##      ##    ##       
##     ## ##     ##  ##  ##     ##  ##   ##     ##    ##       
########  ########   ##  ##     ## ##     ##    ##    ######   
##        ##   ##    ##   ##   ##  #########    ##    ##       
##        ##    ##   ##    ## ##   ##     ##    ##    ##       
##        ##     ## ####    ###    ##     ##    ##    ######## 

    def _append(self, dcm):
        """
        Append a dicomfile (as a dicom.dataset.FileDataset) to the series.
        """
        self._datasets.append(dcm)

    def _sort(self):
        """ sort()
        Sort the datasets by instance number.
        """
        self._datasets.sort(key=lambda k: k.InstanceNumber)

    def _finish(self):
        """
        Evaluate the series of dicom files. Together they should make up
        a volumetric dataset. This means the files should meet certain
        conditions. Also some additional information has to be calculated,
        such as the distance between the slices. This method sets the
        attributes for "shape", "sampling" and "info".

        This method checks:
          * that there are no missing files
          * that the dimensions of all images match
          * that the pixel spacing of all images match
        """
        if len(self._files) > 0:
            dcmFile = dicom.read_file(self._files[0], force=True)

            if "StudyInstanceUID" in dcmFile:
                self._studyInstanceUid = dcmFile.StudyInstanceUID

            self._datasets.append(dcmFile)

            # Extract information about ROIs if possible
            self.prepareRois()

        # # The datasets list should be sorted by instance number
        # L = self._datasets
        # if len(L) == 0:
        #     return
        # elif len(L) < 2:
        #     # Set attributes
        #     ds = self._datasets[0]
        #     self._info = self._datasets[0]
        #     self._shape = [ds.Rows, ds.Columns]
        #     self._sampling = [float(ds.PixelSpacing[0]), float(ds.PixelSpacing[1])]
        #     return

        # # Get previous
        # ds1 = L[0]

        # # Init measures to calculate average of
        # distance_sum = 0.0

        # # Init measures to check (these are in 2D)
        # dimensions = ds1.Rows, ds1.Columns
        # sampling = float(ds1.PixelSpacing[0]), float(ds1.PixelSpacing[1])  # row, column

        # for index in range(len(L)):
        #     # The first round ds1 and ds2 will be the same, for the
        #     # distance calculation this does not matter

        #     # Get current
        #     ds2 = L[index]

        #     # Get positions
        #     pos1 = float(ds1.ImagePositionPatient[2])
        #     pos2 = float(ds2.ImagePositionPatient[2])

        #     # Update distance_sum to calculate distance later
        #     distance_sum += abs(pos1 - pos2)

        #     # Test measures
        #     dimensions2 = ds2.Rows, ds2.Columns
        #     sampling2 = float(ds2.PixelSpacing[0]), float(ds2.PixelSpacing[1])
        #     if dimensions != dimensions2:
        #         # We cannot produce a volume if the dimensions match
        #         raise ValueError('Dimensions of slices does not match.')
        #     if sampling != sampling2:
        #         # We can still produce a volume, but we should notify the user
        #         msg = 'Warning: sampling does not match.'
        #         if self._showProgress is _progressCallback:
        #             _progressBar.PrintMessage(msg)
        #         else:
        #             print msg
        #     # Store previous
        #     ds1 = ds2

        # # Create new dataset by making a deep copy of the first
        # info = dicom.dataset.Dataset()
        # firstDs = self._datasets[0]
        # for key in firstDs.keys():
        #     # Ignore pixel data
        #     if key != (0x7fe0, 0x0010):
        #         el = firstDs[key]
        #         info.add_new(el.tag, el.VR, el.value)

        # # Finish calculating average distance
        # # (Note that there are len(L)-1 distances)
        # distance_mean = distance_sum / (len(L) - 1)

        # # Store information that is specific for the serie
        # self._shape = [len(L), ds2.Rows, ds2.Columns]
        # self._sampling = [distance_mean, float(ds2.PixelSpacing[0]),
        #                   float(ds2.PixelSpacing[1])]

        # # Store
        # self._info = info

    def __repr__(self):
        """Object representation
        """
        adr = hex(id(self)).upper()
        return "<DicomSeries with %i images at %s>" % (len(self._datasets), adr)
