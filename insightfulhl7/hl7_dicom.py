import hl7apy
from hl7apy import parser
from hl7apy.core import Group, Segment, Message, Field
from hl7apy.exceptions import UnsupportedVersion

import pydicom
import argparse
import os


def main():
    my_parser = argparse.ArgumentParser(description='Convert dicom with radiology report to hl7 message')
    my_parser.add_argument('-i', '--input',  type=str, help='input dicom', required=True)
    my_parser.add_argument('-o', '--output',  type=str, help='output hl7', required=True)    
    my_parser.add_argument('-v', '--verbose', dest="verbosity", help="verbose output", action='store_true', default=False)
    args = my_parser.parse_args()

    if not os.path.exists(args.input):
        print(f"Input file {args.input} does not exist.")
        return

    if args.verbosity:
        print(f"Reading DICOM file: {args.input}")    
    dcm = pydicom.dcmread(args.input)

    study_description = dcm.get("StudyDescription")
    accession = dcm.get("AccessionNumber")
    patient_name = dcm.get("PatientName")
    patient_id = dcm.get("PatientID")
    patient_dob = dcm.get("PatientBirthDate")
    patient_sex = dcm.get("PatientSex")
    patient_address = dcm.get("PatientAddress")
    procedure_code_seq = dcm.get("ProcedureCodeSequence")
    procedure_code = procedure_code_seq[0].get("CodeValue")
    body_part = dcm.get("BodyPartExamined")

    #print( f"Procedure Code Sequence: {procedure_code_seq}")


    msg = Message("ORU_R01")

    ts = dcm.get("StudyDate")+dcm.get("StudyTime")
    if args.verbosity:
        print(f"Study Date and Time: {ts}")

    msg.msh.msh_3 = 'PS360'
    msg.msh.msh_4 = 'HUP'
    msg.msh.msh_6 = 'HUP'
    msg.msh.msh_7 = ts
    msg.msh.msh_9 = 'ORU^R01'


    msg.pid.pid_3 = patient_id
    pid_5 = Field('PID_5')
    pid_5.pid_5_1 = patient_name.family_name
    pid_5.pid_5_2 = patient_name.given_name
    pid_5.pid_5_3 = patient_name.middle_name
    msg.pid.add(pid_5)
    msg.pid.pid_7 = patient_dob
    msg.pid.pid_8 = patient_sex
    msg.pid.pid_11 = patient_address

    msg.pv1.pv1_1 = '1'
    msg.pv1.pv1_2 = '0'
    pv1_3 = Field('PV1_3')
    pv1_3.pv1_3_1 = 'PCAMCT+RAD'
    pv1_3.pv1_3_4 = 'HUP'
    pv1_3.pv1_3_7 = 'PCAM'
    pv1_3.pv1_3_9 = 'RAD HUP PCAM GROUND CT'
    msg.pv1.add(pv1_3)
    msg.pv1.pv1_44 = ts

    msg.orc.orc_1 = 'RE'    

    msg.obr.obr_1 = '1'     # Set ID
    #msg.obr.obr_2 =      # Placer Order Number
    msg.obr.obr_3 = accession
    obr_4 = Field('OBR_4')
    obr_4.obr_4_1 = procedure_code
    obr_4.obr_4_2 = study_description
    msg.obr.add(obr_4)
    msg.obr.obr_7 = ts
    msg.obr.obr_22 = ts

    # OBX|1|TX|CTCHEZ&BODY^CT CHEST W IV CONTRAST||INFORMATION: \H\ \N\84-year-old female with history of gastric cancer. Staging.\.br\\.br\PROCEDURE: Contrast enhanced CT of the chest was performed using thin section reconstructions. Chest CT performed with high-resolution technique.\.br\\.br\INTRAVENOUS CONTRAST: 80 ml of IOPAMIDOL 76 % IV SOLN. \.br\\.br\COMPARISON: Chest CT 7/26/2024, FDG PET/CT 5/7/2024.\.br\\.br\FINDINGS:\H\\.br\\N\\.br\LUNGS, PLEURA: \.br\\.br\Central airways are patent.\.br\\.br\No focal consolidation.\.br\\.br\Stable 5 mm right lower lobe pulmonary nodule (5/258), nonavid on PET/CT 5/7/2024 and morphologically a benign intrapulmonary lymph node. No new pulmonary nodules.\.br\\.br\No pleural effusion or pneumothorax.\.br\\.br\CARDIOVASCULAR, MEDIASTINUM, THYROID: \.br\\.br\The heart is top normal in size. No pericardial effusion. Mild coronary artery and aortic valve calcifications. The great vessels are normal in appearance.\.br\\.br\Heterogeneous thyroid gland without dominant nodule.\.br\\.br\Small hiatal hernia. The esophagus is patulous, which may be seen with dysmotility or gastroesophageal reflux. Lower esophagus is thickened and may be related to known cancer or reflux disease\.br\\.br\LYMPH NODES: No thoracic lymphadenopathy\.br\\.br\SKELETON, CHEST WALL: Right chest wall port with tip at the cavoatrial junction. Degenerative changes of the spine. No suspicious osseous lesions.\.br\\.br\UPPER ABDOMEN: A dedicated abdominal CT will be reported separately.\.br\\.br\\H\\.br\\N\||||||F|||20241007161106|||

    obx1 = Segment('OBX')
    obx1.obx_1 = '1'
    obx1.obx_2 = 'TX'
    obx1_id = Field('OBX_3')
    obx1_id.obx_3_1 = procedure_code + '&BODY'
    obx1_id.obx_3_2 = study_description
    obx1.add(obx1_id)
    msg.add(obx1)



# OBX|2|TX|CTCHEZ&IMP^CT CHEST W IV CONTRAST||IMPRESSION:\.br\\.br\1.\X09\No evidence of metastatic disease in the chest.\.br\\.br\\.br\Pulmonary nodule follow-up recommendation:\.br\[LN17O] Continued imaging follow-up with chest CT may be performed per the clinical protocol regarding the primary neoplasm.\.br\\.br\\H\\.br\\N\ATTENDING PHYSICIAN ATTESTATION [ATT05]: I have personally reviewed the images and agree with this report.||||||F|||20241007161106|||


# ZBR||14868037|1649920760^Walsh^John^^^^^^Y^^^|1083845333^Simpson^Scott^^^^^Y^Y^^^||1083845333^Simpson^Scott^^^^^Y^Y^^^|||NOR|Signed^F^N^|20241007143405^20241007161106^20241007143405^0^Radiology^|1649920760^Trans^20241007145639^MJ0HSYSC^20241007145639^Transcribed~1083845333^Signed^20241007161106^MJ0E28JC^20241007161106^Signed|Signed^N|


    





    if args.verbosity:
        print(f"MSH Segment: {msg.msh.value}")
        print(f"PID Segment: {msg.pid.value}")
        print(f"PV1 Segment: {msg.pv1.value}")
        print(f"ORC Segment: {msg.orc.value}")
        print(f"OBR Segment: {msg.obr.value}")
        print(f"OBX Segment: {msg.obx.value}")

if __name__ == "__main__":
    main()