import { Link } from 'react-router-dom';

import { PlaceholderPage } from './PlaceholderPage';

export function WorkspacesPage() {
  return (
    <PlaceholderPage
      title="Workspaces"
      description="The list of workspaces you belong to will appear here."
    >
      <Link className="text-sm font-medium text-blue-600 hover:underline" to="/w/demo">
        Open a sample workspace route
      </Link>
    </PlaceholderPage>
  );
}
