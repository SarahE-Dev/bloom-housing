import { HttpService } from '@nestjs/axios';
import { firstValueFrom } from 'rxjs';
import { ApplicationCreate } from '../dtos/applications/application-create.dto';

export interface ModelInput {
  age: number;
  income: number;
  veteran: boolean;
  benefits: boolean;
  num_people: number;
  disabled: boolean;
}

export const mapDtoToModelInput = (dto: ApplicationCreate): ModelInput => {
  console.log('Mapping DTO to Model Input:', dto);

  const currentYear = new Date().getFullYear();

  // Calculate age
  const age = dto.applicant?.birthYear
    ? Math.max(currentYear - Number(dto.applicant.birthYear), 18)
    : 30;

  // Calculate total number of people (applicant + household members)
  const num_people = dto.householdMember
    ? 1 + dto.householdMember.length // 1 for applicant + household members
    : 1;

  // Check for disabilities
  const disabled = !!(
    dto.accessibility?.mobility ||
    dto.accessibility?.vision ||
    dto.accessibility?.hearing
  );

  // Check for veteran status with options validation
  let veteran = false;
  if (Array.isArray(dto.programs)) {
    console.log('Programs array:', JSON.stringify(dto.programs, null, 2));
    veteran = dto.programs.some((program, index) => {
      // Skip invalid or missing program entries
      if (!program || typeof program !== 'object') {
        console.warn(`Invalid program at index ${index}:`, program);
        return false;
      }
      // Ensure key is a string and claimed is a boolean
      if (typeof program.key !== 'string' || typeof program.claimed !== 'boolean') {
        console.warn(
          `Invalid program key or claimed at index ${index}:`,
          `key=${program.key}, claimed=${program.claimed}`,
        );
        return false;
      }
      // Check if program is veteran-related and claimed
      const isVeteranProgram = program.key.toLowerCase().includes('veteran') && program.claimed === true;
      if (!isVeteranProgram) {
        return false;
      }
      // Check options array for veteran status
      const options = Array.isArray(program.options) ? program.options : [];
      const hasYes = options.some((option) => {
        const isYes = typeof option.key === 'string' && option.key.toLowerCase() === 'yes' && option.checked === true;
        return isYes;
      });
      const hasNo = options.some((option) => {
        const isNo = typeof option.key === 'string' && option.key.toLowerCase() === 'no' && option.checked === true;
        return isNo;
      });
      const veteranStatus = isVeteranProgram && hasYes && !hasNo;
      return veteranStatus;
    });
  } else {
    console.warn('Programs is not an array:', dto.programs);
  }

  // Check for public benefits
  const benefits = !!dto.incomeVouchers;

  // Parse and normalize income
  let income = dto.income
    ? Number(String(dto.income).replace(/[^0-9.]/g, '')) || 0
    : 0;

  if (dto.incomePeriod === 'perMonth') {
    income *= 12;
  }

  const input: ModelInput = {
    age,
    income,
    veteran,
    benefits,
    num_people,
    disabled,
  };

  console.log('Model Input for Flask:', input);

  if (!dto.income) {
    console.warn('Using default for missing field: income');
  }

  return input;
};

export interface ModelPrediction {
  prediction: 'Not at Risk' | 'At Risk';
  probability: number;
}

export const getModelPrediction = async (
  httpService: HttpService,
  input: ModelInput,
): Promise<ModelPrediction> => {
  try {
    const flaskUrl = process.env.FLASK_URL || 'http://localhost:5000';
    const response = await firstValueFrom(
      httpService.post(`${flaskUrl}/predict`, input),
    );
    return {
      prediction: response.data.label,
      probability: response.data.probability,
    };
  } catch (error) {
    console.error('Model Prediction failed:', error.message);
    throw new Error('Model prediction service unavailable');
  }
};