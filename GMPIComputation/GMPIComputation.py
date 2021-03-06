import os
import unittest
import vtk, qt, ctk, slicer
from slicer.ScriptedLoadableModule import *
import logging
import re
import numpy

#########################################################################################
####                                                                                 ####
#### GMPIComputation  ###################################################################
####                                                                                 ####
#########################################################################################
class GMPIComputation(ScriptedLoadableModule):
  """Uses ScriptedLoadableModule base class, available at:
  https://github.com/Slicer/Slicer/blob/master/Base/Python/slicer/ScriptedLoadableModule.py
  """

  def __init__(self, parent):
    ScriptedLoadableModule.__init__(self, parent)
    self.parent.title = "GMPIComputation" # TODO make this more human readable by adding spaces
    self.parent.categories = ["SEEGA"]
    self.parent.dependencies = []
    self.parent.contributors = ["Gabriele Arnulfo (Univ. Genoa) & Massimo Narizzano (Univ. Genoa)"]
    self.parent.helpText = """
    Compute the Gray Matter Proximity Index starting  .....
    """
    self.parent.acknowledgementText = """
    """ 

#########################################################################################
####                                                                                 ####
#### GMPIComputationWidget ########## ###################################################
####                                                                                 ####
#########################################################################################
class GMPIComputationWidget(ScriptedLoadableModuleWidget):

#######################################################################################
### setup 
#######################################################################################
  def setup(self):
    ScriptedLoadableModuleWidget.setup(self)

    self.gmpiCB = ctk.ctkCollapsibleButton()
    self.gmpiCB.text = "GMPI Computation"
    self.layout.addWidget(self.gmpiCB)
    self.gmpiFL = qt.QFormLayout(self.gmpiCB)

    #### Left Pial selection box
    self.leftPialCBox = slicer.qMRMLNodeComboBox()
    self.leftPialCBox.nodeTypes = ( ("vtkMRMLModelNode"), "" )
    self.leftPialCBox.selectNodeUponCreation = True
    self.leftPialCBox.addEnabled = False
    self.leftPialCBox.removeEnabled = False
    self.leftPialCBox.noneEnabled = True
    self.leftPialCBox.showHidden = False
    self.leftPialCBox.showChildNodeTypes = False
    self.leftPialCBox.setMRMLScene( slicer.mrmlScene )
    self.leftPialCBox.setToolTip( "Pick the left pial." )
    self.gmpiFL.addRow("Left Pial: ", self.leftPialCBox)

    #### Left White selection box
    self.leftWhiteCBox = slicer.qMRMLNodeComboBox()
    self.leftWhiteCBox.nodeTypes = ( ("vtkMRMLModelNode"), "" )
    self.leftWhiteCBox.selectNodeUponCreation = True
    self.leftWhiteCBox.addEnabled = False
    self.leftWhiteCBox.removeEnabled = False
    self.leftWhiteCBox.noneEnabled = True
    self.leftWhiteCBox.showHidden = False
    self.leftWhiteCBox.showChildNodeTypes = False
    self.leftWhiteCBox.setMRMLScene( slicer.mrmlScene )
    self.leftWhiteCBox.setToolTip( "Pick the left pial." )
    self.gmpiFL.addRow("Left White: ", self.leftWhiteCBox)

    #### Right Pial selection box
    self.rightPialCBox = slicer.qMRMLNodeComboBox()
    self.rightPialCBox.nodeTypes = ( ("vtkMRMLModelNode"), "" )
    self.rightPialCBox.selectNodeUponCreation = True
    self.rightPialCBox.addEnabled = False
    self.rightPialCBox.removeEnabled = False
    self.rightPialCBox.noneEnabled = True
    self.rightPialCBox.showHidden = False
    self.rightPialCBox.showChildNodeTypes = False
    self.rightPialCBox.setMRMLScene( slicer.mrmlScene )
    self.rightPialCBox.setToolTip( "Pick the right pial." )
    self.gmpiFL.addRow("Right Pial: ", self.rightPialCBox)

    #### Right White selection box
    self.rightWhiteCBox = slicer.qMRMLNodeComboBox()
    self.rightWhiteCBox.nodeTypes = ( ("vtkMRMLModelNode"), "" )
    self.rightWhiteCBox.selectNodeUponCreation = True
    self.rightWhiteCBox.addEnabled = False
    self.rightWhiteCBox.removeEnabled = False
    self.rightWhiteCBox.noneEnabled = True
    self.rightWhiteCBox.showHidden = False
    self.rightWhiteCBox.showChildNodeTypes = False
    self.rightWhiteCBox.setMRMLScene( slicer.mrmlScene )
    self.rightWhiteCBox.setToolTip( "Pick the right pial." )
    self.gmpiFL.addRow("Right White: ", self.rightWhiteCBox)

    #### Fiducials list Combo Box
    self.fiducialsCBox = slicer.qMRMLNodeComboBox()
    self.fiducialsCBox.nodeTypes = ( ("vtkMRMLMarkupsFiducialNode"), "" )
    self.fiducialsCBox.selectNodeUponCreation = False
    self.fiducialsCBox.addEnabled = False
    self.fiducialsCBox.removeEnabled = False
    self.fiducialsCBox.noneEnabled = True
    self.fiducialsCBox.setMRMLScene( slicer.mrmlScene )
    self.fiducialsCBox.setToolTip("Select a fiducial list")
    self.gmpiFL.addRow("Fiducial : ", self.fiducialsCBox)

    # GMPI Computation Detection button
    self.gmpiPB = qt.QPushButton("Apply")
    self.gmpiPB.toolTip = "Run the algorithm."
    self.gmpiPB.enabled = True

    #### Aggiungo il bottone al layout
    self.gmpiFL.addRow(self.gmpiPB)

    # connections
    self.gmpiPB.connect('clicked(bool)', self.onGMPIComputation)

#######################################################################################
###  onGMPIComputation
#######################################################################################
  def onGMPIComputation(self):
    slicer.util.showStatusMessage("START GMPI Computation")
    print "RUN GMPI Computation"
    GMPIComputationLogic().runGMPIComputation(self.fiducialsCBox.currentNode(),\
                                              self.leftPialCBox.currentNode(),\
                                              self.rightPialCBox.currentNode(),\
                                              self.leftWhiteCBox.currentNode(),\
                                              self.rightWhiteCBox.currentNode())


    print "END GMPI Computation"
    slicer.util.showStatusMessage("END GMPI Computation")

#########################################################################################
####                                                                                 ####
#### GMPIComputationLogic  ##############################################################
####                                                                                 ####
#########################################################################################
class GMPIComputationLogic(ScriptedLoadableModuleLogic):
  """
  """
#######################################################################################
###  __init___
#######################################################################################
  def __init__(self):
    # Create a Progress Bar
    self.pb = qt.QProgressBar()

#######################################################################################
###  findTheNearestVertex
#######################################################################################
  def findNearestVertex(self,contact, surfaceVertices):
      dist = numpy.sqrt( numpy.sum( (contact - surfaceVertices)**2,axis=1) )
      return surfaceVertices[ dist.argmin(),:]

#######################################################################################
###  computeGMPI
#######################################################################################
  def computeGmpi(self,contact,pial,white):
      return (numpy.dot( (contact-white) , (pial - white) ) / numpy.linalg.norm((pial - white))**2 )

#######################################################################################
###  runGMPIComputation
#######################################################################################
  def runGMPIComputation(self,fids,leftPial,rightPial,leftWhite,rightWhite):

    # Check that the Fiducial has been selected
    if (fids == None):
      # notify error
      slicer.util.showStatusMessage("Error, No Fiducial selected")
      return

    # LEFT/RIGHT PIAL/WHITE must be selected
    if ((leftPial == None) or (rightPial == None) or \
        (leftWhite == None) or (rightWhite == None)):
      # notify error
      slicer.util.showStatusMessage("Error, please select the four volumes!")
      return

    # Set the parameters of the progess bar and show it 
    self.pb.setRange(0,fids.GetNumberOfFiducials())
    self.pb.show()
    self.pb.setValue(0)
    slicer.app.processEvents()

    # Compute GMPI for each fiducial
    for i in xrange(fids.GetNumberOfFiducials()):
      # update progress bar
      self.pb.setValue(i+1)
      slicer.app.processEvents()

      # Only for Active Fiducial points the GMPI is computed
      if fids.GetNthFiducialSelected(i) == True:

        # Check if it is a left or right channel, by reading the contact
        # label. If the label contain the '(prime) char then the contact
        # is in the left emisphere, right otherwise
        #[TODO]: better way to do it? 
        chLabel = fids.GetNthFiducialLabel(i)
        if re.search('^\w\d+',chLabel) is None:
          # left channel
          pial = leftPial.GetPolyData()
          white = leftWhite.GetPolyData()
        else:
          # right channel
          pial = rightPial.GetPolyData()
          white = rightWhite.GetPolyData()
          
        # [TODO] : ????
        pialVertices = vtk.util.numpy_support.vtk_to_numpy(pial.GetPoints().GetData())
        whiteVertices = vtk.util.numpy_support.vtk_to_numpy(white.GetPoints().GetData())

        # istantiate the variable which holds the point
        currContactCentroid = [0,0,0]

        # copy current position from FiducialList
        fids.GetNthFiducialPosition(i,currContactCentroid)

        # find nearest vertex coordinates
        pialNearVtx = self.findNearestVertex(currContactCentroid,pialVertices)
        whiteNearVtx = self.findNearestVertex(currContactCentroid,whiteVertices)
      
        # print ",".join([str(pialNearVtx),str(whiteNearVtx),str(currContactCentroid)])
        gmpi=float("{0:.3f}".format(self.computeGmpi(currContactCentroid,pialNearVtx,whiteNearVtx)))
        print "gmpi: "+ str(gmpi)
        self.descr = fids.GetNthMarkupDescription(i)
        fids.SetNthMarkupDescription(i,' '.join([self.descr,'GMPI:',str(gmpi),';']))
    
