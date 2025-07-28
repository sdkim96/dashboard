import { 
  FiCommand, 
  FiUsers, 
  FiTrendingUp, 
  FiZap, 
  FiHeart, 
  FiBriefcase, 
  FiCompass, 
  FiLayers, 
  FiCpu, 
  FiGlobe 
} from 'react-icons/fi';

export type Departments = 'Common' | 'HR' | 'Sales' | 'Marketing' | 'CustomerSupport' | 'Finance' | 'Planning' | 'BusinessSupport' | 'ProductDevelopment' | 'InternationalSales'

export const DEPARTMENT_ICONS: Record<string, any> = {
  Common: FiCommand,
  HR: FiUsers,
  Sales: FiTrendingUp,
  Marketing: FiZap,
  CustomerSupport: FiHeart,
  Finance: FiBriefcase,
  Planning: FiCompass,
  BusinessSupport: FiLayers,
  ProductDevelopment: FiCpu,
  InternationalSales: FiGlobe,
};

// 부서별 스타일 정의
export const DEPARTMENTS_STYLES: Record<Departments, { id: string; color: string; name: string; bgGradient: string }> = {
  Common: {
    id: "Common",
    color: 'blue',
    name: 'Common',
    bgGradient: 'linear(to-r, blue.400, blue.600)',
  },
  HR: {
    id: "HR",
    color: 'green',
    name: 'HR',
    bgGradient: 'linear(to-r, green.400, green.600)',
  },
  Sales: {
    id: "Sales",
    color: 'orange',
    name: 'Sales',
    bgGradient: 'linear(to-r, orange.400, orange.600)',
  },
  Marketing: {
    id: "Marketing",
    color: 'purple',
    name: 'Marketing',
    bgGradient: 'linear(to-r, purple.400, purple.600)',
  },
  CustomerSupport: {
    id: "CustomerSupport",
    color: 'teal',
    name: 'Customer Support',
    bgGradient: 'linear(to-r, teal.400, teal.600)',
  },
  Finance: {
    id: "Finance",
    color: 'yellow',
    name: 'Finance',
    bgGradient: 'linear(to-r, yellow.400, yellow.600)',
  },
  Planning: {
    id: "Planning",
    color: 'pink',
    name: 'Planning',
    bgGradient: 'linear(to-r, pink.400, pink.600)',
  },
  BusinessSupport: {
    id: "BusinessSupport",
    color: 'cyan',
    name: 'Business Support',
    bgGradient: 'linear(to-r, cyan.400, cyan.600)',
  },
  ProductDevelopment: {
    id: "ProductDevelopment",
    color: 'gray',
    name: 'Product Development',
    bgGradient: 'linear(to-r, gray.400, gray.600)',
  },
  InternationalSales: {
    id: "InternationalSales",
    color: 'red',
    name: 'International Sales',
    bgGradient: 'linear(to-r, red.400, red.600)',
  },
};