"""
Workflow module tests
"""

import os
import tempfile
import unittest

from txtai.embeddings import Documents, Embeddings
from txtai.pipeline import Summary, Translation, Textractor
from txtai.workflow import Workflow, Task, FileTask, ImageTask, RetrieveTask, StorageTask, WorkflowTask

# pylint: disable = C0411
from utils import Utils


class TestWorkflow(unittest.TestCase):
    """
    Workflow tests
    """

    def testBaseWorkflow(self):
        """
        Tests a basic workflow
        """

        translate = Translation()

        # Workflow that translate text to Spanish
        workflow = Workflow([Task(lambda x: translate(x, "es"))])

        results = list(workflow(["The sky is blue", "Forest through the trees"]))

        self.assertEqual(len(results), 2)

    def testComplexWorkflow(self):
        """
        Tests a complex workflow
        """

        textractor = Textractor(paragraphs=True, minlength=150, join=True)
        summary = Summary("t5-small")

        embeddings = Embeddings({"path": "sentence-transformers/nli-mpnet-base-v2"})
        documents = Documents()

        def index(x):
            documents.add(x)
            return x

        # Extract text and summarize articles
        articles = Workflow([FileTask(textractor), Task(lambda x: summary(x, maxlength=15))])

        # Complex workflow that extracts text, runs summarization then loads into an embeddings index
        tasks = [WorkflowTask(articles, r".\.pdf$"), Task(index, unpack=False)]

        data = ["file://" + Utils.PATH + "/article.pdf", "Workflows can process audio files, documents and snippets"]

        # Convert file paths to data tuples
        data = [(x, element, None) for x, element in enumerate(data)]

        # Execute workflow, discard results as they are streamed
        workflow = Workflow(tasks)
        for _ in workflow(data):
            pass

        # Build the embeddings index
        embeddings.index(documents)

        # Cleanup temporary storage
        documents.close()

        # Run search and validate result
        index, _ = embeddings.search("search text", 1)[0]
        self.assertEqual(index, 0)

    def testExtractWorkflow(self):
        """
        Tests column extraction tasks
        """

        workflow = Workflow([Task(lambda x: x, unpack=False, column=0)], batch=1)

        results = list(workflow([(0, 1)]))
        self.assertEqual(results[0], 0)

        results = list(workflow([(0, (1, 2), None)]))
        self.assertEqual(results[0], (0, 1, None))

        results = list(workflow([1]))
        self.assertEqual(results[0], 1)

    def testImageWorkflow(self):
        """
        Tests an image task
        """

        workflow = Workflow([ImageTask()])

        results = list(workflow([Utils.PATH + "/books.jpg"]))

        self.assertEqual(results[0].size, (1024, 682))

    def testMergeWorkflow(self):
        """
        Tests merge tasks
        """

        task = Task([lambda x: [pow(y, 2) for y in x], lambda x: [pow(y, 3) for y in x]], merge="hstack")

        # Test hstack (column-wise) merge
        workflow = Workflow([task])
        results = list(workflow([2]))
        self.assertEqual(results, [(4, 8)])

        # Test vstack (row-wise) merge
        task.merge = "vstack"
        workflow = Workflow([task])
        results = list(workflow([2]))
        self.assertEqual(results, [4, 8])

        # Test concat (values joined into single string) merge
        task.merge = "concat"
        workflow = Workflow([task])
        results = list(workflow([2]))
        self.assertEqual(results, ["4. 8"])

        # Test generated (id, data, tag) tuples are properly returned
        workflow = Workflow([Task(lambda x: [(0, y, None) for y in x])])
        results = list(workflow([(1, "text", "tags")]))
        self.assertEqual(results[0], (0, "text", None))

    def testRetrieveWorkflow(self):
        """
        Tests a retrieve task
        """

        # Test retrieve with generated temporary directory
        workflow = Workflow([RetrieveTask()])
        results = list(workflow(["file://" + Utils.PATH + "/books.jpg"]))
        self.assertTrue(results[0].endswith("books.jpg"))

        # Test retrieve with specified temporary directory
        workflow = Workflow([RetrieveTask(directory=os.path.join(tempfile.gettempdir(), "retrieve"))])
        results = list(workflow(["file://" + Utils.PATH + "/books.jpg"]))
        self.assertTrue(results[0].endswith("books.jpg"))

    def testStorageWorkflow(self):
        """
        Tests a storage task
        """

        workflow = Workflow([StorageTask()])

        results = list(workflow(["local://" + Utils.PATH]))

        self.assertEqual(len(results), 18)
