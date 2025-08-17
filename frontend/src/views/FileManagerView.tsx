// src/views/FileManagerView.tsx
import React, { useEffect, useMemo, useRef, useState } from 'react';
import {
  Box, Text, VStack, HStack, SimpleGrid, Card, CardBody, Badge, Button,
  IconButton, useToast, Input, InputGroup, InputLeftElement, Wrap, WrapItem,
  Modal, ModalOverlay, ModalContent, ModalHeader, ModalBody, ModalFooter, ModalCloseButton,
  useDisclosure, Divider, Tooltip, Skeleton, SkeletonText, Center, Alert, AlertIcon, Spinner, Link
} from '@chakra-ui/react';
import {
  HiCloudUpload, HiSearch, HiTrash, HiSparkles, HiInformationCircle,
  HiUser, HiCalendar, HiLink, HiDocumentText, HiDatabase
} from 'react-icons/hi';

// 정확한 API import
import {
  uploadFileApiV1FilesUploadPost,
  getFilesApiV1FilesGet,
  vectorizeFilesApiV1FilesFileIdVectorizePost,
  deleteFileApiV1FilesFileIdDelete,
} from '../client';

// 타입 import (서버 File ↔ DOM File 충돌 방지 위해 alias)
import type {
  File as ServerFile,
  GetFilesResponse,
  PostFileUploadResponse,
  PostVectorizeFilesResponse,
  DeleteFilesByIdResponse
} from '../client';

const formatBytes = (bytes: number) => {
  if (!bytes && bytes !== 0) return '-';
  const sizes = ['Bytes', 'KB', 'MB', 'GB', 'TB'];
  if (bytes === 0) return '0 Byte';
  const i = Math.floor(Math.log(bytes) / Math.log(1024));
  return `${(bytes / Math.pow(1024, i)).toFixed(1)} ${sizes[i]}`;
};

const formatDate = (iso?: string) => {
  if (!iso) return '-';
  try {
    return new Date(iso).toLocaleString();
  } catch {
    return iso;
  }
};

// 상태 메타 (주석 정의에 따라 색상/라벨 매핑)
// RED: Failed, YELLOW: In progress, GREEN: Succeeded, GRAY: Not started
const getStatusMeta = (status: ServerFile['vectorizing_status']) => {
  switch (status) {
    case 'yellow': return { label: 'In progress', colorScheme: 'yellow' as const };
    case 'green':  return { label: 'Ready',       colorScheme: 'green'  as const };
    case 'red':    return { label: 'Failed',      colorScheme: 'red'    as const };
    default:       return { label: 'Not started', colorScheme: 'gray'   as const };
  }
};

const FileManagerView: React.FC = () => {
  const [files, setFiles] = useState<ServerFile[]>([]);
  const [loading, setLoading] = useState(true);
  const [uploading, setUploading] = useState(false);
  const [search, setSearch] = useState('');
  const [selected, setSelected] = useState<ServerFile | null>(null);

  // 로컬 피드백용 (API 응답 전/중/후)
  const [vectorizing, setVectorizing] = useState<Record<string, boolean>>({});
  const [justVectorized, setJustVectorized] = useState<Record<string, boolean>>({});

  const { isOpen, onOpen, onClose } = useDisclosure();
  const toast = useToast();
  const inputRef = useRef<HTMLInputElement>(null);

  useEffect(() => {
    refreshList();
  }, []);

  const refreshList = async () => {
    setLoading(true);
    try {
      const res = await getFilesApiV1FilesGet({});
      const data = (res.data as GetFilesResponse);
      setFiles(data.files ?? []);
    } catch (e) {
      console.error(e);
      toast({
        title: 'Failed to load files',
        status: 'error',
        duration: 3000,
        isClosable: true
      });
    } finally {
      setLoading(false);
    }
  };

  const onPickFile = () => inputRef.current?.click();

  const onUpload = async (file: File) => {
    setUploading(true);
    try {
      // form-data key: "file"
      const res = await uploadFileApiV1FilesUploadPost({
        body: { file },
      });
      const data = res.data as PostFileUploadResponse;
      toast({
        title: 'Uploaded',
        description: `file_id: ${data.file_id}`,
        status: 'success',
        duration: 3000,
        isClosable: true
      });
      await refreshList();
    } catch (e: any) {
      console.error(e);
      toast({
        title: 'Upload failed',
        description: e?.message ?? 'Please try again.',
        status: 'error',
        duration: 3500,
        isClosable: true
      });
    } finally {
      setUploading(false);
    }
  };

  // 드래그&드랍
  const [dragOver, setDragOver] = useState(false);
  const onDrop: React.DragEventHandler<HTMLDivElement> = async (ev) => {
    ev.preventDefault();
    setDragOver(false);
    const dropped = ev.dataTransfer.files;
    if (dropped && dropped.length > 0) {
      await onUpload(dropped[0]);
    }
  };

  const filtered = useMemo(() => {
    if (!search) return files;
    const q = search.toLowerCase();
    return files.filter(f =>
      f.file_name.toLowerCase().includes(q) ||
      f.file_extension.toLowerCase().includes(q) ||
      f.file_content_type.toLowerCase().includes(q) ||
      f.file_id.toLowerCase().includes(q)
    );
  }, [files, search]);

  const handleVectorize = async (file: ServerFile) => {
    // 노란불이거나 로컬 진행중이면 클릭 무시
    if (file.vectorizing_status === 'yellow' || vectorizing[file.file_id]) return;

    setVectorizing(prev => ({ ...prev, [file.file_id]: true }));
    try {
      const res = await vectorizeFilesApiV1FilesFileIdVectorizePost({
        path: { file_id: file.file_id },
      });
      const _data = res.data as PostVectorizeFilesResponse;

      // UX 피드백
      setJustVectorized(prev => ({ ...prev, [file.file_id]: true }));
      toast({
        title: 'Vectorization started',
        description: 'Your document is being processed.',
        status: 'info',
        duration: 2500,
        isClosable: true
      });

      // 잠깐 Done 뱃지 노출
      setTimeout(() => {
        setJustVectorized(prev => ({ ...prev, [file.file_id]: false }));
      }, 2000);

      // 서버 상태가 바뀌었을 수 있으니 목록 갱신(옵션)
      await refreshList();

    } catch (e: any) {
      console.error(e);
      toast({
        title: 'Vectorization failed',
        description: e?.message ?? 'Please check the file type/size.',
        status: 'error',
        duration: 3500,
        isClosable: true
      });
    } finally {
      setVectorizing(prev => ({ ...prev, [file.file_id]: false }));
    }
  };

  const handleDelete = async (file: ServerFile) => {
    try {
      const res = await deleteFileApiV1FilesFileIdDelete({
        path: { file_id: file.file_id }
      });
      const data = res.data as DeleteFilesByIdResponse;
      toast({
        title: 'Deleted',
        description: `file_id: ${data.file_id}`,
        status: 'success',
        duration: 2500,
        isClosable: true
      });
      setFiles(prev => prev.filter(f => f.file_id !== file.file_id));
    } catch (e: any) {
      console.error(e);
      toast({
        title: 'Delete failed',
        description: e?.message ?? 'Please try again.',
        status: 'error',
        duration: 3500,
        isClosable: true
      });
    }
  };

  return (
    <Box p={6} minH="100vh">
      <VStack spacing={8} align="stretch">

        {/* Header */}
        <VStack spacing={2} align="stretch">
          <HStack justify="space-between" align="start">
            <VStack align="start" spacing={1}>
              <Text fontSize="3xl" fontWeight="bold">
                Files
              </Text>
              <Text color="gray.600" fontSize="md">
                Upload, browse, vectorize, and manage your documents
              </Text>
            </VStack>
            <Badge colorScheme="blue" variant="subtle" px={3} py={1} fontSize="sm">
              {files.length} files
            </Badge>
          </HStack>

          {/* Search */}
          <InputGroup maxW="400px">
            <InputLeftElement pointerEvents="none">
              <HiSearch color="gray.400" />
            </InputLeftElement>
            <Input
              placeholder="Search by name, extension, content-type, or file_id"
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              borderRadius="md"
            />
          </InputGroup>
        </VStack>

        {/* Upload Box */}
        <Box
          p={6}
          border="2px dashed"
          borderColor={dragOver ? 'blue.300' : 'gray.300'}
          borderRadius="lg"
          bg={dragOver ? 'blue.50' : 'gray.50'}
          transition="all 0.2s ease"
          onDragOver={(e) => { e.preventDefault(); setDragOver(true); }}
          onDragLeave={() => setDragOver(false)}
          onDrop={onDrop}
        >
          <VStack spacing={4}>
            <HiCloudUpload size={28} />
            <Text fontWeight="semibold">Drag & drop your file here</Text>
            <Text fontSize="sm" color="gray.600">or</Text>
            <HStack>
              <Input
                type="file"
                ref={inputRef}
                display="none"
                onChange={async (e) => {
                  const file = e.target.files?.[0];
                  if (file) await onUpload(file);
                  e.currentTarget.value = '';
                }}
              />
              <Button onClick={onPickFile} isLoading={uploading} loadingText="Uploading">
                Choose file
              </Button>
            </HStack>
          </VStack>
        </Box>

        {/* Files Grid */}
        {loading ? (
          <SimpleGrid columns={{ base: 1, md: 2, lg: 3 }} spacing={4}>
            {Array.from({ length: 6 }).map((_, i) => (
              <Card key={i}>
                <CardBody>
                  <Skeleton height="20px" mb={2} />
                  <SkeletonText noOfLines={3} spacing="3" />
                </CardBody>
              </Card>
            ))}
          </SimpleGrid>
        ) : filtered.length > 0 ? (
          <SimpleGrid columns={{ base: 1, md: 2, lg: 3 }} spacing={4}>
            {filtered.map((f) => {
              const meta = getStatusMeta(f.vectorizing_status);
              const isProcessing = f.vectorizing_status === 'yellow' || !!vectorizing[f.file_id];
              const isJustDone = !!justVectorized[f.file_id];

              return (
                <Card key={f.file_id} borderWidth="1px" position="relative" overflow="hidden">
                  {/* 진행 중 오버레이 */}
                  {isProcessing && (
                    <Box
                      position="absolute"
                      inset={0}
                      bg="blackAlpha.400"
                      display="flex"
                      alignItems="center"
                      justifyContent="center"
                      zIndex={1}
                    >
                      <VStack spacing={2} color="white">
                        <Spinner thickness="3px" />
                        <Text fontSize="sm" fontWeight="semibold">Vectorizing…</Text>
                      </VStack>
                    </Box>
                  )}

                  <CardBody opacity={isProcessing ? 0.6 : 1} transition="opacity 0.2s">
                    <VStack align="stretch" spacing={3}>
                      <HStack justify="space-between" align="start">
                        <VStack align="start" spacing={0}>
                          <HStack spacing={2}>
                            <Text fontWeight="bold" noOfLines={1}>{f.file_name}</Text>
                            {isJustDone && <Badge colorScheme="green">Done</Badge>}
                            <Badge colorScheme={meta.colorScheme}>{meta.label}</Badge>
                          </HStack>
                          <HStack fontSize="xs" color="gray.600" spacing={2}>
                            <Badge colorScheme="gray" variant="subtle">{f.file_extension}</Badge>
                            <Text>•</Text>
                            <Text>{formatBytes(f.file_size)}</Text>
                          </HStack>
                        </VStack>

                        <Wrap>
                          <WrapItem>
                            <Tooltip label="Details" hasArrow>
                              <IconButton
                                aria-label="Details"
                                icon={<HiInformationCircle />}
                                size="sm"
                                variant="ghost"
                                onClick={() => { setSelected(f); onOpen(); }}
                                isDisabled={isProcessing}
                              />
                            </Tooltip>
                          </WrapItem>

                          {/* 벡터화 버튼: yellow(진행중)일 때 숨김 */}
                          {f.vectorizing_status !== 'yellow' && f.vectorizing_status !== 'green' &&(
                            <WrapItem>
                              <Tooltip label="Vectorize" hasArrow>
                                <IconButton
                                  aria-label="Vectorize"
                                  icon={<HiSparkles />}
                                  size="sm"
                                  colorScheme="purple"
                                  variant="ghost"
                                  onClick={() => handleVectorize(f)}
                                  isLoading={isProcessing}
                                  isDisabled={isProcessing}
                                />
                              </Tooltip>
                            </WrapItem>
                          )}

                          <WrapItem>
                            <Tooltip label="Delete" hasArrow>
                              <IconButton
                                aria-label="Delete"
                                icon={<HiTrash />}
                                size="sm"
                                colorScheme="red"
                                variant="ghost"
                                onClick={() => handleDelete(f)}
                                isDisabled={isProcessing}
                              />
                            </Tooltip>
                          </WrapItem>
                        </Wrap>
                      </HStack>

                      <Divider />

                      {/* 카드 하단 메타(간단 표기) */}
                      <VStack align="start" spacing={1} fontSize="sm" color="gray.700">
                        <HStack><Text w="120px" color="gray.500">content-type</Text><Text>{f.file_content_type}</Text></HStack>
                        <HStack><Text w="120px" color="gray.500">author</Text><Text>{f.author_name}</Text></HStack>
                        <HStack><Text w="120px" color="gray.500">created</Text><Text>{formatDate(f.created_at)}</Text></HStack>
                      </VStack>
                    </VStack>
                  </CardBody>
                </Card>
              );
            })}
          </SimpleGrid>
        ) : (
          <Center py={16}>
            <VStack spacing={3}>
              <Alert status="info" borderRadius="md">
                <AlertIcon />
                No files found. Upload a file to get started.
              </Alert>
              <Button onClick={onPickFile} leftIcon={<HiCloudUpload />}>Upload</Button>
            </VStack>
          </Center>
        )}
      </VStack>

      {/* Details Modal */}
      <Modal isOpen={isOpen} onClose={onClose} size="lg" scrollBehavior="inside">
        <ModalOverlay />
        <ModalContent>
          <ModalHeader>{selected?.file_name}</ModalHeader>
          <ModalCloseButton />
          <ModalBody>
            {selected ? (
              <VStack align="stretch" spacing={4}>
                {/* 제목 + 확장자/사이즈(아이콘 포함) */}
                <VStack align="stretch" spacing={1}>
                  <Text fontSize="lg" fontWeight="bold">{selected.file_id}</Text>
                </VStack>

                <Divider />

                {/* 아이콘과 함께 표시되는 상세 메타 */}
                <VStack align="stretch" spacing={3} fontSize="sm">
                  <HStack spacing={1}>
                      <HiDatabase />
                      <Text>{formatBytes(selected.file_size)}</Text>
                    </HStack>
                  <HStack>
                    <HiLink />
                    <Link wordBreak="break-all">{selected.file_path}</Link>
                  </HStack>
                  <HStack>
                    <HiDocumentText />
                    <Text>{selected.file_extension}</Text>
                  </HStack>
                  <HStack>
                    <HiUser />
                    <Text>{selected.author_name}</Text>
                  </HStack>
                  <HStack>
                    <HiCalendar />
                    <Text>{formatDate(selected.created_at)}</Text>
                  </HStack>
                </VStack>
              </VStack>
            ) : (
              <SkeletonText noOfLines={5} spacing="3" />
            )}
          </ModalBody>
          <ModalFooter>
            <Button variant="ghost" onClick={onClose}>Close</Button>
          </ModalFooter>
        </ModalContent>
      </Modal>
    </Box>
  );
};

export default FileManagerView;