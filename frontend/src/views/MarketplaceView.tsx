import React, { useState, useEffect } from 'react';
import {
  Box,
  Text,
  SimpleGrid,
  Card,
  CardBody,
  CardHeader,
  Badge,
  Button,
  HStack,
  VStack,
  Avatar,
  Flex,
  Modal,
  ModalOverlay,
  ModalContent,
  ModalHeader,
  ModalFooter,
  ModalBody,
  ModalCloseButton,
  useDisclosure,
  Input,
  InputGroup,
  InputLeftElement,
  Alert,
  AlertIcon,
  Divider,
  Wrap,
  WrapItem,
  useToast,
  Skeleton,
  SkeletonText
} from '@chakra-ui/react';
import { HiSearch, HiStar, HiDownload, HiUser, HiCalendar, HiTag } from 'react-icons/hi';

// 정확한 API import
import { 
  getAvailableAgentsApiV1AgentsGet,
  getAgentApiV1AgentsAgentIdVersionAgentVersionGet,
  subscribeAgentApiV1AgentsAgentIdVersionAgentVersionSubscribePost
} from '../client';

// 정확한 타입 import
import type {
  AgentMarketPlace,
  AgentDetail,
  GetAvailableAgentsResponse,
  GetAgentResponse,
  PostSubscribeAgentResponse
} from '../client';

// 카드 컴포넌트 Props
interface AgentCardProps {
  agent: AgentMarketPlace;
  onCardClick: (agent: AgentMarketPlace) => void;
}

const AgentCard: React.FC<AgentCardProps> = ({ agent, onCardClick }) => {
  const isSubscribed = agent.subscribed || false;
  
  return (
    <Card
      cursor="pointer"
      transition="all 0.2s"
      _hover={{
        transform: 'translateY(-2px)',
        boxShadow: 'lg'
      }}
      onClick={() => onCardClick(agent)}
      h="200px"
      bg={isSubscribed ? "gray.50" : "white"}
      borderColor={isSubscribed ? "gray.300" : "gray.200"}
      borderWidth="1px"
    >
      <CardHeader pb={2}>
        <Flex align="center" justify="space-between">
          <HStack spacing={3}>
            <Avatar
              size="sm"
              name={agent.name}
              src={agent.icon_link || undefined}
              bg={isSubscribed ? "gray.400" : "blue.500"}
            />
            <VStack align="start" spacing={0} flex={1}>
              <Text fontSize="md" fontWeight="bold" noOfLines={1}>
                {agent.name}
              </Text>
              <HStack spacing={2}>
                <Badge size="sm" colorScheme="gray">
                  v{agent.agent_version}
                </Badge>
                {isSubscribed && (
                  <Badge size="sm" colorScheme="green" variant="solid">
                    ✓ Subscribed
                  </Badge>
                )}
              </HStack>
            </VStack>
          </HStack>
        </Flex>
      </CardHeader>

      <CardBody pt={0}>
        <VStack align="stretch" spacing={3}>
          {/* Tags */}
          {agent.tags && agent.tags.length > 0 && (
            <Wrap spacing={1}>
              {agent.tags.slice(0, 3).map((tag, index) => (
                <WrapItem key={index}>
                  <Badge size="sm" colorScheme="blue" variant="subtle">
                    {tag}
                  </Badge>
                </WrapItem>
              ))}
              {agent.tags.length > 3 && (
                <WrapItem>
                  <Badge size="sm" colorScheme="gray" variant="subtle">
                    +{agent.tags.length - 3}
                  </Badge>
                </WrapItem>
              )}
            </Wrap>
          )}

          <Flex justify="space-between" align="center">
            <HStack spacing={4} fontSize="sm" color="gray.600">
              <HStack spacing={1}>
                <HiStar />
                <Text>4.8</Text>
              </HStack>
              <HStack spacing={1}>
                <HiDownload />
                <Text>1.2k</Text>
              </HStack>
            </HStack>
          </Flex>
        </VStack>
      </CardBody>
    </Card>
  );
};

interface AgentDetailModalProps {
  isOpen: boolean;
  onClose: () => void;
  agent: AgentMarketPlace | null;
}

const AgentDetailModal: React.FC<AgentDetailModalProps> = ({ 
  isOpen, 
  onClose, 
  agent 
}) => {
  const [agentDetail, setAgentDetail] = useState<AgentDetail | null>(null);
  const [loading, setLoading] = useState(false);
  const [subscribing, setSubscribing] = useState(false);
  const [isSubscribed, setIsSubscribed] = useState(false);
  const toast = useToast();

  useEffect(() => {
    if (isOpen && agent) {
      setIsSubscribed(agent.subscribed || false);
      fetchAgentDetail(agent.agent_id, agent.agent_version);
    }
  }, [isOpen, agent]);

  const fetchAgentDetail = async (agentId: string, agentVersion: number) => {
    setLoading(true);
    try {
      const response = await getAgentApiV1AgentsAgentIdVersionAgentVersionGet({
        path: { 
          agent_id: agentId, 
          agent_version: agentVersion 
        }
      });
      
      if (response.data && response.data.agent) {
        setAgentDetail(response.data.agent);
      }
    } catch (error) {
      console.error('Failed to fetch agent detail:', error);
      toast({
        title: 'Error',
        description: 'Failed to load agent details',
        status: 'error',
        duration: 3000,
        isClosable: true,
      });
    } finally {
      setLoading(false);
    }
  };

  const handleSubscribe = async () => {
    if (!agent) return;
    
    setSubscribing(true);
    try {
      const response = await subscribeAgentApiV1AgentsAgentIdVersionAgentVersionSubscribePost({
        path: { 
          agent_id: agent.agent_id, 
          agent_version: agent.agent_version 
        }
      });
      
      if (response.data && response.data.status === 'success') {
        setIsSubscribed(true);
        toast({
          title: 'Success',
          description: response.data.message || 'Successfully subscribed to agent',
          status: 'success',
          duration: 3000,
          isClosable: true,
        });
      }
    } catch (error) {
      console.error('Failed to subscribe:', error);
      toast({
        title: 'Error',
        description: 'Failed to subscribe to agent',
        status: 'error',
        duration: 3000,
        isClosable: true,
      });
    } finally {
      setSubscribing(false);
    }
  };

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric'
    });
  };

  return (
    <Modal isOpen={isOpen} onClose={onClose} size="xl" scrollBehavior="inside">
      <ModalOverlay />
      <ModalContent>
        <ModalHeader>
          {loading ? (
            <Skeleton height="32px" width="200px" />
          ) : (
            <HStack spacing={3}>
              <Avatar
                size="md"
                name={agentDetail?.name || agent?.name}
                src={agentDetail?.icon_link || agent?.icon_link || undefined}
                bg="blue.500"
              />
              <VStack align="start" spacing={0}>
                <Text fontSize="xl" fontWeight="bold">
                  {agentDetail?.name || agent?.name}
                </Text>
                <Text fontSize="sm" color="gray.600">
                  by {agentDetail?.author_name || 'Unknown'}
                </Text>
              </VStack>
            </HStack>
          )}
        </ModalHeader>
        
        <ModalCloseButton />
        
        <ModalBody>
          {loading ? (
            <VStack spacing={4} align="stretch">
              <SkeletonText mt="4" noOfLines={3} spacing="4" />
              <Skeleton height="20px" />
              <SkeletonText noOfLines={2} spacing="4" />
            </VStack>
          ) : agentDetail ? (
            <VStack spacing={6} align="stretch">
              {/* Basic Info */}
              <VStack align="stretch" spacing={3}>
                <Text fontSize="md" lineHeight="1.6">
                  {agentDetail.description}
                </Text>
                
                <HStack spacing={4} fontSize="sm" color="gray.600">
                  <HStack spacing={1}>
                    <HiUser />
                    <Text>Version {agentDetail.agent_version}</Text>
                  </HStack>
                  <HStack spacing={1}>
                    <HiCalendar />
                    <Text>{formatDate(agentDetail.created_at)}</Text>
                  </HStack>
                </HStack>
              </VStack>

              {/* Tags */}
              {agentDetail.tags && agentDetail.tags.length > 0 && (
                <VStack align="stretch" spacing={2}>
                  <HStack spacing={1}>
                    <HiTag />
                    <Text fontSize="sm" fontWeight="semibold">Tags</Text>
                  </HStack>
                  <Wrap spacing={2}>
                    {agentDetail.tags.map((tag, index) => (
                      <WrapItem key={index}>
                        <Badge colorScheme="blue" variant="subtle">
                          {tag}
                        </Badge>
                      </WrapItem>
                    ))}
                  </Wrap>
                </VStack>
              )}

              <Divider />

              {/* Prompt/Instructions */}
              {agentDetail.prompt && (
                <VStack align="stretch" spacing={2}>
                  <Text fontSize="sm" fontWeight="semibold">
                    Instructions
                  </Text>
                  <Box
                    p={4}
                    bg="gray.50"
                    borderRadius="md"
                    border="1px"
                    borderColor="gray.200"
                  >
                    <Text fontSize="sm" whiteSpace="pre-wrap">
                      {agentDetail.prompt}
                    </Text>
                  </Box>
                </VStack>
              )}

              {/* Stats */}
              <HStack justify="space-around" p={4} bg="gray.50" borderRadius="md">
                <VStack spacing={1}>
                  <HStack spacing={1} color="orange.500">
                    <HiStar />
                    <Text fontWeight="bold">4.8</Text>
                  </HStack>
                  <Text fontSize="xs" color="gray.600">Rating</Text>
                </VStack>
                <VStack spacing={1}>
                  <HStack spacing={1} color="blue.500">
                    <HiDownload />
                    <Text fontWeight="bold">1.2k</Text>
                  </HStack>
                  <Text fontSize="xs" color="gray.600">Downloads</Text>
                </VStack>
                <VStack spacing={1}>
                  <Text fontWeight="bold" color="green.500">
                    Free
                  </Text>
                  <Text fontSize="xs" color="gray.600">Price</Text>
                </VStack>
              </HStack>
            </VStack>
          ) : (
            <Alert status="error">
              <AlertIcon />
              Failed to load agent details
            </Alert>
          )}
        </ModalBody>

        <ModalFooter>
          <HStack spacing={3}>
            <Button variant="ghost" onClick={onClose}>
              Close
            </Button>
            {agent && (
              <Button
                colorScheme={isSubscribed ? "gray" : "blue"}
                variant="solid"
                onClick={handleSubscribe}
                isLoading={subscribing}
                loadingText={isSubscribed ? "Unsubscribing..." : "Subscribing..."}
                leftIcon={isSubscribed ? <Text>✓</Text> : undefined}
              >
                {isSubscribed ? "Subscribed" : "Subscribe"}
              </Button>
            )}
          </HStack>
        </ModalFooter>
      </ModalContent>
    </Modal>
  );
};

const MarketplaceView: React.FC = () => {
  const [agents, setAgents] = useState<AgentMarketPlace[]>([]);
  const [loading, setLoading] = useState(true);
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedAgent, setSelectedAgent] = useState<AgentMarketPlace | null>(null);
  const { isOpen, onOpen, onClose } = useDisclosure();

  useEffect(() => {
    fetchAgents();
  }, []);

  const fetchAgents = async (search?: string) => {
    setLoading(true);
    try {
      const response = await getAvailableAgentsApiV1AgentsGet({
        query: {
          search: search || null,
          page: 1,
          size: 20
        }
      });
      
      if (response.data && response.data.agents) {
        setAgents(response.data.agents);
      }
    } catch (error) {
      console.error('Failed to fetch agents:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleSearch = (value: string) => {
    setSearchQuery(value);
    fetchAgents(value);
  };

  const handleCardClick = (agent: AgentMarketPlace) => {
    setSelectedAgent(agent);
    onOpen();
  };

  const filteredAgents = agents.filter(agent =>
    agent.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
    agent.tags?.some(tag => tag.toLowerCase().includes(searchQuery.toLowerCase()))
  );

  return (
    <Box p={6}>
      {/* Header */}
      <VStack spacing={6} align="stretch">
        <VStack spacing={4} align="stretch">
          <Text fontSize="2xl" fontWeight="bold">
            Agent Marketplace
          </Text>
          <Text color="gray.600">
            Discover and subscribe to AI agents for your projects
          </Text>
          
          {/* Search Bar */}
          <InputGroup maxW="500px">
            <InputLeftElement pointerEvents="none">
              <HiSearch color="gray.400" />
            </InputLeftElement>
            <Input
              placeholder="Search agents by name or tags..."
              value={searchQuery}
              onChange={(e) => handleSearch(e.target.value)}
            />
          </InputGroup>
        </VStack>

        {/* Agent Grid */}
        {loading ? (
          <SimpleGrid columns={{ base: 1, md: 2, lg: 3, xl: 4 }} spacing={6}>
            {Array.from({ length: 8 }).map((_, index) => (
              <Card key={index} h="200px">
                <CardBody>
                  <VStack spacing={3} align="stretch">
                    <HStack spacing={3}>
                      <Skeleton width="40px" height="40px" borderRadius="full" />
                      <VStack align="start" spacing={1} flex={1}>
                        <Skeleton height="20px" width="60%" />
                        <Skeleton height="16px" width="40%" />
                      </VStack>
                    </HStack>
                    <SkeletonText noOfLines={2} spacing="2" />
                    <HStack justify="space-between">
                      <Skeleton height="16px" width="30%" />
                      <Skeleton height="16px" width="30%" />
                    </HStack>
                  </VStack>
                </CardBody>
              </Card>
            ))}
          </SimpleGrid>
        ) : filteredAgents.length > 0 ? (
          <SimpleGrid columns={{ base: 1, md: 2, lg: 3, xl: 4 }} spacing={6}>
            {filteredAgents.map((agent) => (
              <AgentCard
                key={`${agent.agent_id}-v${agent.agent_version}`}
                agent={agent}
                onCardClick={handleCardClick}
              />
            ))}
          </SimpleGrid>
        ) : (
          <Box textAlign="center" py={12}>
            <Text fontSize="lg" color="gray.500">
              No agents found matching your search
            </Text>
          </Box>
        )}
      </VStack>

      {/* Agent Detail Modal */}
      <AgentDetailModal
        isOpen={isOpen}
        onClose={onClose}
        agent={selectedAgent}
      />
    </Box>
  );
};

export default MarketplaceView;