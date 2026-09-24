import { useParams } from 'react-router-dom';

import { PlaceholderPage } from './PlaceholderPage';

export function WorkspacePage() {
  const { workspaceId } = useParams<{ workspaceId: string }>();

  return (
    <PlaceholderPage
      title="Workspace"
      description={`The sponsorship table for workspace "${workspaceId}" will render here.`}
    />
  );
}
