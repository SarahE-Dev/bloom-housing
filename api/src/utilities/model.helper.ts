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

export const mapDtoToModelInput = (
  dto: ApplicationCreate,
  threshold: number = 0.5,
): ModelInput => {
  console.log('Mapping DTO to Model Input:', dto);

  const currentYear = new Date().getFullYear();

  // Calculate age
  const age = dto.applicant?.birthYear
    ? Math.max(currentYear - Number(dto.applicant.birthYear), 18)
    : 30;

  // Calculate adult kids (ages 18–21)
  const adultKids = dto.householdMember
    ? dto.householdMember.filter(
        (member) =>
          member.birthYear &&
          currentYear - Number(member.birthYear) >= 18 &&
          currentYear - Number(member.birthYear) <= 21,
      ).length
    : 0;

  // Check for disabilities
  const disabled = !!(
    dto.accessibility?.mobility ||
    dto.accessibility?.vision ||
    dto.accessibility?.hearing
  );

  // Check for veteran status
  const veteran = Array.isArray(dto.programs)
    ? dto.programs.some(
        (program) =>
          typeof program.key === 'string' &&
          program.key.toLowerCase().includes('veteran') &&
          program.claimed === true,
      )
    : false;

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
    adult_kids: adultKids,
    disabled,
    threshold,
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
