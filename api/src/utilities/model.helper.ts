import { HttpService } from '@nestjs/axios';
import { firstValueFrom } from 'rxjs';
import { ApplicationCreate } from '../dtos/applications/application-create.dto';

export interface ModelInput {
  age: number;
  income: number;
  veteran: boolean;
  benefits: boolean;
  adult_kids: number;
  disabled: boolean;
  threshold?: number;
}

export const mapDtoToModelInput = (dto: ApplicationCreate, threshold: number = 0.5): ModelInput => {
  console.log('Mapping DTO to Model Input:', dto);

  // Calculate age from applicant.birthYear
  const currentYear = new Date().getFullYear();
  const age = dto.applicant?.birthYear
    ? Math.max(currentYear - Number(dto.applicant.birthYear), 18) // Ensure age ≥ 18
    : 30; // Default

  // Calculate adult_kids from householdMember
  const adultKids = dto.householdMember
    ? dto.householdMember.filter(
        (member) =>
          member.birthYear &&
          currentYear - Number(member.birthYear) >= 18 && Number(member.birthYear) <= 21,
      ).length
    : 0;

  // Determine disabled from accessibility
  const disabled = !!(
    dto.accessibility?.mobility ||
    dto.accessibility?.vision ||
    dto.accessibility?.hearing
  );

  // Derive veteran from programs
  const veteran = Array.isArray(dto.programs)
    ? dto.programs.some(
        (program) =>
          program.key?.toLowerCase() === 'veteran' && program.claimed,
      )
    : false;

  // Derive benefits from incomeVouchers or programs
  const assistancePrograms = ['snap', 'section 8', 'assistance']; // Adjust as needed
  const benefitsFromPrograms = Array.isArray(dto.programs)
    ? dto.programs.some(
        (program) =>
          program.key?.toLowerCase() &&
          assistancePrograms.some((ap) =>
            program.key.toLowerCase().includes(ap),
          ) && program.claimed,
      )
    : false;
  const benefits = dto.incomeVouchers || benefitsFromPrograms;

  // Parse income, removing any non-numeric characters (e.g., "$")
  const income = dto.income
    ? Number(String(dto.income).replace(/[^0-9.]/g, '')) || 0
    : 0;

  const input = {
    age,
    income,
    veteran,
    benefits,
    adult_kids: adultKids,
    disabled,
    threshold,
  };

  console.log('Model Input for Flask:', input);

  // Warn about defaults
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
    return { prediction: response.data.label, probability: response.data.probability }
  } catch (error) {
    console.error('Model Prediction failed:', error.message);
    throw new Error('Model prediction service unavailable');
  }
};