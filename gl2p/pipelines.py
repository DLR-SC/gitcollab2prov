from dataclasses import dataclass
from typing import List, Tuple

from prov.model import ProvDocument

from .api import GitLabAPIClient
from .models import CommitModel, CommitResourceModel, ResourceModel
from .procs import (CommitProcessor, CommitResourceProcessor,
                    IssueResourceProcessor, MergeRequestResourceProcessor)
from .procs.meta import (CommitModelPackage, ParseableContainer,
                         ResourceModelPackage)
from .utils.types import Commit, Diff, Issue, MergeRequest


@dataclass
class CommitPipeline:
    """
    Pipeline that fetches, processes and models git commits of a project.
    """
    project_id: str
    client: GitLabAPIClient

    async def fetch(self) -> Tuple[List[Commit], List[Diff]]:
        """
        Retrieve commits and their diffs from the project API wrapper.
        """
        async with self.client as clt:
            commits = await clt.commits()
            diffs = await clt.commit_diffs()

        return commits, diffs

    def process(self, commits: List[Commit], diffs: List[Diff]) -> List[CommitModelPackage]:
        """
        Return list of commit model packages.
        """
        proc = CommitProcessor(commits, diffs)
        return proc.run()

    def create_model(self, resources: List[CommitModelPackage]) -> ProvDocument:
        """
        Return populated PROV graph for resource model.
        """
        model = CommitModel(self.project_id)

        for resource in resources:
            model.push(resource)

        return model.document()


@dataclass
class CommitResourcePipeline:
    """
    Pipeline that fetches, processes and models project commits.
    """
    project_id: str
    client: GitLabAPIClient

    async def fetch(self) -> Tuple[List[Commit], ParseableContainer]:
        """
        Retrieve commits and their notes from the project API wrapper.
        """
        async with self.client as clt:
            commits = await clt.commits()
            notes = await clt.commit_notes()

        return commits, ParseableContainer(notes=notes)

    def process(self, commits: List[Commit], parseables: ParseableContainer) -> List[ResourceModelPackage]:
        """
        Return list of resource model packages.
        """
        proc = CommitResourceProcessor(commits, parseables)
        return proc.run()

    def create_model(self, resources: List[ResourceModelPackage]) -> ProvDocument:
        """
        Return populated PROV graph for resource model.
        """
        model = CommitResourceModel(self.project_id)

        for resource in resources:
            model.push(resource)

        return model.document()


@dataclass
class IssueResourcePipeline:
    """
    Pipeline that fetches, processes and models project issues.
    """
    project_id: str
    client: GitLabAPIClient

    async def fetch(self) -> Tuple[List[Issue], ParseableContainer]:
        """
        Retrieve issues, their labels, their awards, their notes and
        the awards of all notes from the project API wrapper.
        """
        async with self.client as clt:
            issues = await clt.issues()
            labels = await clt.issue_labels()
            awards = await clt.issue_awards()
            notes = await clt.issue_notes()
            note_awards = await clt.issue_note_awards()

        return issues, ParseableContainer(labels, awards, notes, note_awards)

    def process(self, issues: List[Issue], parseables: ParseableContainer) -> List[ResourceModelPackage]:
        """
        Return list of resource model packages.
        """
        proc = IssueResourceProcessor(issues, parseables)
        return proc.run()

    def create_model(self, resources: List[ResourceModelPackage]) -> ProvDocument:
        """
        Return populated PROV graph for resource model.
        """
        model = ResourceModel(self.project_id)

        for resource in resources:
            model.push(resource)

        return model.document()


@dataclass
class MergeRequestResourcePipeline:
    """
    Pipeline that fetches, processes and models project merge requests.
    """
    project_id: str
    client: GitLabAPIClient

    async def fetch(self) -> Tuple[List[MergeRequest], ParseableContainer]:
        """
        Retrieve merge requests, their labels, their awards, their
        notes and all awards for each note from the project API wrapper.
        """
        async with self.client as clt:
            merge_requests = await clt.merge_requests()
            labels = await clt.merge_request_labels()
            awards = await clt.merge_request_awards()
            notes = await clt.merge_request_notes()
            note_awards = await clt.merge_request_note_awards()

        return merge_requests, ParseableContainer(labels, awards, notes, note_awards)

    def process(self, merge_requests: List[MergeRequest], parseables: ParseableContainer) -> List[ResourceModelPackage]:
        """
        Return list of resource model packages.
        """
        proc = MergeRequestResourceProcessor(merge_requests, parseables)
        return proc.run()

    def create_model(self, resources: List[ResourceModelPackage]) -> ProvDocument:
        """
        Return populated PROV graph for resource model.
        """
        model = ResourceModel(self.project_id)

        for resource in resources:
            model.push(resource)

        return model.document()
